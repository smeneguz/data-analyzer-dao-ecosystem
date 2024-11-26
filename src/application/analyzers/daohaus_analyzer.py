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