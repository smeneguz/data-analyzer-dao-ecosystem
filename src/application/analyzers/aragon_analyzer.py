# src/application/analyzers/aragon_analyzer.py
from typing import Dict
import pandas as pd
import os
from datetime import datetime
from ...domain.interfaces.platform_analyzer import PlatformAnalyzer

class AragonAnalyzer(PlatformAnalyzer):
    def get_organization_stats(self, platform_files: Dict) -> Dict:
        """
        Calculate organization statistics for Aragon DAOs.
        """
        try:
            # Load required files
            dfs = self._load_dataframes(platform_files)
            
            # Basic organization count from organizations.csv
            total_orgs = len(dfs['organizations'])
            
            # Convert timestamp strings to datetime objects
            dfs['organizations']['createdAt'] = pd.to_numeric(dfs['organizations']['createdAt'])
            dfs['transactions']['date'] = pd.to_numeric(dfs['transactions']['date'])
            
            # Convert to datetime
            dfs['organizations']['createdAt'] = pd.to_datetime(dfs['organizations']['createdAt'], unit='s')
            dfs['transactions']['date'] = pd.to_datetime(dfs['transactions']['date'], unit='s')
            
            # Get unique organization addresses
            org_addresses = set(dfs['organizations']['orgAddress'].unique())
            org_with_tx = set(dfs['transactions']['orgAddress'].unique())
            
            # Calculate active organizations (those with transactions)
            active_orgs = len(org_addresses & org_with_tx)
            
            # Current time for age calculations
            current_time = pd.Timestamp.now()
            
            # Calculate activity metrics
            activity_metrics = self._calculate_activity_metrics(
                dfs, 
                current_time
            )
            
            return {
                "total_organizations": total_orgs,
                "active_organizations": active_orgs,
                "inactive_organizations": total_orgs - active_orgs,
                **activity_metrics
            }
            
        except Exception as e:
            raise Exception(f"Error in Aragon analysis: {str(e)}")
        

    
    def get_dao_details(self, platform_files: Dict, search_address: str) -> Dict:
        dfs = self._load_dataframes(platform_files)
        
        details = {
            "basic_info": {},
            "membership": {},
            "proposals": {},
            "voting": {},
            "treasury": {}
        }
        
        # Basic info
        org = dfs['organizations'][dfs['organizations']['orgAddress'] == search_address]
        if len(org) == 0:
            raise ValueError(f"Organization not found: {search_address}")
        
        details["basic_info"] = {
            "name": org.iloc[0].get('name', 'Unnamed'),
            "address": search_address,
            "created_at": pd.to_datetime(org.iloc[0]['createdAt'], unit='s'),
            "network": org.iloc[0]['network']
        }

        # Membership info
        if 'tokenHolders' in dfs:
            holders = dfs['tokenHolders'][dfs['tokenHolders']['organizationAddress'] == search_address].copy()
            holders.loc[:, 'balance'] = holders['balance'].astype('float64')
            details["membership"] = {
                "total_members": len(holders['address'].unique()),
                "active_members": len(holders[holders['balance'] > 0]['address'].unique())
            }
            if 'miniMeTokens' in dfs:
                tokens = dfs['miniMeTokens'][dfs['miniMeTokens']['orgAddress'] == search_address]
                if not tokens.empty:
                    details["membership"]["total_token_supply"] = format(float(tokens['totalSupply'].iloc[0]), '.2e')

        # Proposals/Votes
        if 'votes' in dfs:
            votes = dfs['votes'][dfs['votes']['orgAddress'] == search_address]
            total_votes = len(votes)
            executed = votes['executed'].fillna(False)
            details["proposals"] = {
                "total_proposals": total_votes,
                "passed_proposals": int(executed.sum()),
                "failed_proposals": total_votes - int(executed.sum())
            }
            
            if not votes.empty:
                recent = votes.sort_values('startDate', ascending=False).head(5)
                details["proposals"]["recent"] = []
                for _, vote in recent.iterrows():
                    try:
                        yea = format(float(vote.get('yea', 0)), '.2e')
                        nay = format(float(vote.get('nay', 0)), '.2e')
                        details["proposals"]["recent"].append({
                            "type": f"Vote (Yes: {yea} / No: {nay})",
                            "status": "Passed" if vote['executed'] else "Failed",
                            "created_at": pd.to_datetime(vote['startDate'], unit='s')
                        })
                    except (ValueError, TypeError):
                        continue

        # Voting info
        if 'casts' in dfs:
            casts = dfs['casts'][dfs['casts']['orgAddress'] == search_address]
            supports = casts['supports'].fillna(False)
            details["voting"] = {
                "total_votes_cast": len(casts),
                "unique_voters": len(casts['voter'].unique()),
                "support_votes": int(supports.sum()),
                "against_votes": len(supports) - int(supports.sum())
            }

        # Treasury
        if 'transactions' in dfs:
            tx = dfs['transactions'][dfs['transactions']['orgAddress'] == search_address].copy()
            if not tx.empty:
                tx.loc[:, 'amount'] = tx['amount'].astype('float64')
                details["treasury"] = {"token_balances": []}
                
                for token, group in tx.groupby('token'):
                    incoming = group[group['isIncoming']]['amount'].sum()
                    outgoing = group[~group['isIncoming']]['amount'].sum()
                    balance = incoming - outgoing
                    if balance != 0:
                        details["treasury"]["token_balances"].append({
                            "token": token,
                            "balance": format(balance, '.2e'),
                            "usd_value": 0
                        })

        return details

    def _load_dataframes(self, platform_files: Dict) -> Dict[str, pd.DataFrame]:
        """Load dataframes with optional file handling."""
        required_files = {
            'organizations': platform_files.get('organizations'),
        }
        optional_files = {
            'apps': platform_files.get('apps'),
            'transactions': platform_files.get('transactions'),
            'votes': platform_files.get('votes'),
            'miniMeTokens': platform_files.get('miniMeTokens'),
            'tokenHolders': platform_files.get('tokenHolders')
        }
        
        dataframes = {}
        
        # Load required files
        for name, path in required_files.items():
            if not path or not os.path.exists(path):
                raise Exception(f"Required file not found: {name}")
            dataframes[name] = pd.read_csv(path)
        
        # Load optional files
        for name, path in optional_files.items():
            if path and os.path.exists(path):
                try:
                    dataframes[name] = pd.read_csv(path)
                except Exception as e:
                    print(f"Warning: Could not read optional file {name}: {str(e)}")
        
        return dataframes

    def _calculate_activity_metrics(self, 
                                  dfs: Dict[str, pd.DataFrame],
                                  current_time: pd.Timestamp) -> Dict:
        metrics = {
            "highly_active": 0,
            "moderately_active": 0,
            "minimally_active": 0,
            "potential_test": 0,
            "active_organizations": 0,
            "inactive_organizations": 0,
            "detailed_activity": {
                "highly_active_daos": [],
                "moderately_active_daos": []
            }
        }
        
        for _, dao in dfs['organizations'].iterrows():
            org_address = dao['orgAddress']
            org_name = dao['name'] if 'name' in dao and dao['name'] else 'Unnamed'
            
            # Get organization's transactions
            org_tx = dfs['transactions'][
                dfs['transactions']['orgAddress'] == org_address
            ]
            
            # Calculate metrics
            tx_count = len(org_tx)
            creation_date = dao['createdAt']
            age_days = (current_time - creation_date).days
            
            if tx_count > 0:
                last_tx_date = org_tx['date'].max()
                days_since_last_tx = (current_time - last_tx_date).days
            else:
                days_since_last_tx = age_days

            # Categorize DAO
            if age_days < 7 and tx_count <= 2:
                metrics["potential_test"] += 1
            elif tx_count > 0:
                dao_info = {
                    'address': org_address,
                    'name': org_name,
                    'tx_count': tx_count,
                    'last_activity': last_tx_date if tx_count > 0 else creation_date,
                    'age_days': age_days
                }
                
                if days_since_last_tx <= 30 and tx_count >= 5:
                    metrics["highly_active"] += 1
                    metrics["detailed_activity"]["highly_active_daos"].append(dao_info)
                elif days_since_last_tx <= 90:
                    metrics["moderately_active"] += 1
                    metrics["detailed_activity"]["moderately_active_daos"].append(dao_info)
                else:
                    metrics["minimally_active"] += 1
                metrics["active_organizations"] += 1
            else:
                metrics["inactive_organizations"] += 1
                
        return metrics