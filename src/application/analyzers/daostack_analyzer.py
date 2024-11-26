# src/application/analyzers/daostack_analyzer.py
from typing import Dict
import pandas as pd
import os
from datetime import datetime
from ...domain.interfaces.platform_analyzer import PlatformAnalyzer

class DAOstackAnalyzer(PlatformAnalyzer):
    def get_organization_stats(self, platform_files: Dict) -> Dict:
        """
        Calculate organization statistics for DAOstack.
        Considers:
        - DAO creation and registration
        - Proposal activity
        - Reputation distribution
        - Stake activity
        - Voting patterns
        """
        try:
            # Load required files
            dfs = self._load_dataframes(platform_files)
            
            # Convert timestamps
            timestamp_columns = {
                'proposals': ['createdAt', 'executedAt'],
                'votes': ['createdAt'],
                'stakes': ['createdAt']
            }
            
            for df_name, columns in timestamp_columns.items():
                for col in columns:
                    if col in dfs[df_name].columns:
                        dfs[df_name][col] = pd.to_numeric(dfs[df_name][col])
                        dfs[df_name][col] = pd.to_datetime(dfs[df_name][col], unit='s')
            
            # Basic counts
            total_daos = len(dfs['daos'])
            
            # Current time for calculations
            current_time = pd.Timestamp.now()
            
            # Calculate activity metrics
            activity_metrics = self._calculate_activity_metrics(dfs, current_time)
            
            return {
                "total_organizations": total_daos,
                **activity_metrics
            }
            
        except Exception as e:
            raise Exception(f"Error in DAOstack analysis: {str(e)}")

    def _load_dataframes(self, platform_files: Dict) -> Dict[str, pd.DataFrame]:
        """Load required dataframes."""
        required_files = {
            'daos': platform_files.get('daos'),
            'proposals': platform_files.get('proposals'),
            'votes': platform_files.get('votes'),
            'stakes': platform_files.get('stakes'),
            'reputationHolders': platform_files.get('reputationHolders')
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
        """Calculate detailed activity metrics for DAOstack organizations."""
        metrics = {
            "highly_active": 0,
            "moderately_active": 0,
            "minimally_active": 0,
            "potential_test": 0,
            "active_organizations": 0,
            "inactive_organizations": 0
        }
        
        for _, dao in dfs['daos'].iterrows():
            dao_address = dao['dao']
            
            # Get DAO's activities
            dao_proposals = dfs['proposals'][dfs['proposals']['dao'] == dao_address]
            dao_votes = dfs['votes'][dfs['votes']['dao'] == dao_address]
            dao_stakes = dfs['stakes'][dfs['stakes']['dao'] == dao_address]
            dao_reputation = dfs['reputationHolders'][
                dfs['reputationHolders']['dao'] == dao_address
            ]
            
            # Calculate metrics
            proposal_count = len(dao_proposals)
            vote_count = len(dao_votes)
            stake_count = len(dao_stakes)
            reputation_holder_count = len(dao_reputation)
            
            # Get latest activity
            latest_dates = []
            if not dao_proposals.empty:
                latest_dates.append(dao_proposals['createdAt'].max())
            if not dao_votes.empty:
                latest_dates.append(dao_votes['createdAt'].max())
            if not dao_stakes.empty:
                latest_dates.append(dao_stakes['createdAt'].max())
            
            days_since_last_activity = 999999
            if latest_dates:
                last_activity = max(latest_dates)
                days_since_last_activity = (current_time - last_activity).days
            
            # Categorize DAO
            if proposal_count <= 2 and vote_count <= 2 and reputation_holder_count <= 2:
                metrics["potential_test"] += 1
            elif days_since_last_activity != 999999:
                # Different criteria for DAOstack based on its governance model
                if (days_since_last_activity <= 30 and 
                    (proposal_count >= 3 or vote_count >= 5 or stake_count >= 5)):
                    metrics["highly_active"] += 1
                elif (days_since_last_activity <= 90 and 
                      (proposal_count >= 1 or vote_count >= 3 or stake_count >= 3)):
                    metrics["moderately_active"] += 1
                else:
                    metrics["minimally_active"] += 1
                metrics["active_organizations"] += 1
            else:
                metrics["inactive_organizations"] += 1
            
        return metrics