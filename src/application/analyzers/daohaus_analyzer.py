# src/application/analyzers/daohaus_analyzer.py
from typing import Dict
import pandas as pd
import os
from datetime import datetime
from ...domain.interfaces.platform_analyzer import PlatformAnalyzer

class DAOhausAnalyzer(PlatformAnalyzer):
    def get_organization_stats(self, platform_files: Dict) -> Dict:
        """
        Calculate organization statistics for DAOhaus.
        Considers:
        - Moloch DAO creation and activity
        - Member participation
        - Proposal activity
        - RageQuits
        - Token balances
        """
        try:
            # Load required files
            dfs = self._load_dataframes(platform_files)
            
            # Convert timestamps
            dfs['moloches']['createdAt'] = pd.to_numeric(dfs['moloches']['createdAt'])
            dfs['proposals']['createdAt'] = pd.to_numeric(dfs['proposals']['createdAt'])
            dfs['votes']['createdAt'] = pd.to_numeric(dfs['votes']['createdAt'])
            
            # Convert to datetime
            for df_name in ['moloches', 'proposals', 'votes']:
                dfs[df_name]['createdAt'] = pd.to_datetime(dfs[df_name]['createdAt'], unit='s')
            
            # Basic counts
            total_daos = len(dfs['moloches'])
            
            # Current time for calculations
            current_time = pd.Timestamp.now()
            
            # Calculate activity metrics
            activity_metrics = self._calculate_activity_metrics(dfs, current_time)
            
            return {
                "total_organizations": total_daos,
                **activity_metrics
            }
            
        except Exception as e:
            raise Exception(f"Error in DAOhaus analysis: {str(e)}")

    def _load_dataframes(self, platform_files: Dict) -> Dict[str, pd.DataFrame]:
        """Load required dataframes."""
        required_files = {
            'moloches': platform_files.get('moloches'),
            'proposals': platform_files.get('proposals'),
            'votes': platform_files.get('votes'),
            'members': platform_files.get('members'),
            'rageQuits': platform_files.get('rageQuits')
        }
        
        dataframes = {}
        for name, path in required_files.items():
            if not path or not os.path.exists(path):
                raise Exception(f"Required file not found: {name}")
            try:
                dataframes[name] = pd.read_csv(path)
            except Exception as e:
                raise Exception(f"Error reading {name}: {str(e)}")
                
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
        
        for _, dao in dfs['moloches'].iterrows():
            moloch_address = dao['molochAddress']
            dao_name = dao['name'] if 'name' in dao and dao['name'] else 'Unnamed'
            
            # Get DAO's activities
            dao_proposals = dfs['proposals'][
                dfs['proposals']['molochAddress'] == moloch_address
            ]
            dao_votes = dfs['votes'][
                dfs['votes']['molochAddress'] == moloch_address
            ]
            dao_members = dfs['members'][
                dfs['members']['molochAddress'] == moloch_address
            ]
            
            # Calculate metrics
            proposal_count = len(dao_proposals)
            vote_count = len(dao_votes)
            member_count = len(dao_members)
            
            # Get latest activity
            latest_dates = []
            if not dao_proposals.empty:
                latest_dates.append(dao_proposals['createdAt'].max())
            if not dao_votes.empty:
                latest_dates.append(dao_votes['createdAt'].max())
            
            days_since_last_activity = 999999
            last_activity = None
            if latest_dates:
                last_activity = max(latest_dates)
                days_since_last_activity = (current_time - last_activity).days
            
            dao_info = {
                'address': moloch_address,
                'name': dao_name,
                'proposal_count': proposal_count,
                'vote_count': vote_count,
                'member_count': member_count,
                'last_activity': last_activity or dao['createdAt']
            }
            
            if proposal_count <= 2 and vote_count <= 2 and member_count <= 2:
                metrics["potential_test"] += 1
            elif days_since_last_activity != 999999:
                if days_since_last_activity <= 30 and (proposal_count >= 5 or vote_count >= 10):
                    metrics["highly_active"] += 1
                    metrics["detailed_activity"]["highly_active_daos"].append(dao_info)
                elif days_since_last_activity <= 90:
                    metrics["moderately_active"] += 1
                    metrics["detailed_activity"]["moderately_active_daos"].append(dao_info)
                else:
                    metrics["minimally_active"] += 1
                metrics["active_organizations"] += 1
            else:
                metrics["inactive_organizations"] += 1
                
        return metrics
    


    def get_dao_details(self, platform_files: Dict, search_address: str) -> Dict:
        """Get detailed information about a specific DAOhaus DAO."""
        dfs = self._load_dataframes(platform_files)
        
        details = {
            "basic_info": {},
            "membership": {},
            "proposals": {},
            "voting": {},
            "ragequits": {},
            "treasury": {}
        }
        
        # Basic DAO info
        moloch = dfs['moloches'][dfs['moloches']['molochAddress'] == search_address]
        if len(moloch) == 0:
            raise ValueError(f"DAO not found: {search_address}")
            
        details["basic_info"] = {
            "name": moloch.iloc[0]['name'],
            "address": search_address,
            "created_at": pd.to_datetime(moloch.iloc[0]['createdAt'], unit='s'),
            "version": moloch.iloc[0]['version'],
            "total_shares": moloch.iloc[0]['totalShares'],
            "total_loot": moloch.iloc[0]['totalLoot']
        }
        
        # Membership analysis
        members = dfs['members'][dfs['members']['molochAddress'] == search_address]
        details["membership"] = {
            "total_members": len(members),
            "active_members": len(members[members['exists'] == True]),
            "total_shares_distributed": members['shares'].sum(),
            "total_loot_distributed": members['loot'].sum()
        }
        
        # Proposal analysis
        proposals = dfs['proposals'][dfs['proposals']['molochAddress'] == search_address]
        details["proposals"] = {
            "total_proposals": len(proposals),
            "passed_proposals": len(proposals[proposals['didPass'] == True]),
            "failed_proposals": len(proposals[proposals['didPass'] == False]),
            "sponsored_proposals": len(proposals[proposals['sponsored'] == True])
        }
        
        # Get recent proposals
        recent_proposals = proposals.sort_values('createdAt', ascending=False).head(5)
        details["proposals"]["recent"] = recent_proposals.apply(
            lambda x: {
                "id": x['proposalId'],
                "type": eval(x['details'])['proposalType'] if pd.notna(x['details']) else "Unknown",
                "status": "Passed" if x['didPass'] else "Failed",
                "created_at": pd.to_datetime(x['createdAt'], unit='s')
            }, axis=1
        ).tolist()
        
        # Voting analysis
        votes = dfs['votes'][dfs['votes']['molochAddress'] == search_address]
        details["voting"] = {
            "total_votes": len(votes),
            "unique_voters": len(votes['memberAddress'].unique())
        }
        
        # RageQuit analysis
        ragequits = dfs['rageQuits'][dfs['rageQuits']['molochAddress'] == search_address]
        details["ragequits"] = {
            "total_ragequits": len(ragequits),
            "total_shares_ragequit": ragequits['shares'].sum(),
            "total_loot_ragequit": ragequits['loot'].sum()
        }
        
        # Treasury analysis
        if 'tokenBalances' in dfs:
            balances = dfs['tokenBalances'][dfs['tokenBalances']['molochAddress'] == search_address]
            details["treasury"] = {
                "token_balances": balances.apply(
                    lambda x: {
                        "token": x['symbol'],
                        "balance": x['balanceFloat'],
                        "usd_value": x['usdValue']
                    }, axis=1
                ).tolist()
            }
        
        return details