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
                org_addresses, 
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

    def _load_dataframes(self, platform_files: Dict) -> Dict[str, pd.DataFrame]:
        """
        Load required dataframes.
        """
        required_files = {
            'organizations': platform_files.get('organizations'),
            'transactions': platform_files.get('transactions')
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
                                  org_addresses: set,
                                  current_time: pd.Timestamp) -> Dict:
        """
        Calculate detailed activity metrics for organizations.
        """
        metrics = {
            "highly_active": 0,
            "moderately_active": 0,
            "minimally_active": 0,
            "test_orgs": 0
        }
        
        for org_address in org_addresses:
            # Get organization's transactions
            org_tx = dfs['transactions'][
                dfs['transactions']['orgAddress'] == org_address
            ]
            
            # Get organization creation date
            org_info = dfs['organizations'][
                dfs['organizations']['orgAddress'] == org_address
            ]
            
            if len(org_info) == 0:
                continue
                
            creation_date = org_info['createdAt'].iloc[0]
            
            # Calculate metrics
            age_days = (current_time - creation_date).days
            tx_count = len(org_tx)
            
            if tx_count > 0:
                last_tx_date = org_tx['date'].max()
                days_since_last_tx = (current_time - last_tx_date).days
            else:
                days_since_last_tx = age_days
            
            # Categorize organization
            if age_days < 7 and tx_count <= 2:
                metrics["test_orgs"] += 1
            elif tx_count > 0:  # Only categorize if there are transactions
                if days_since_last_tx <= 30 and tx_count >= 5:
                    metrics["highly_active"] += 1
                elif days_since_last_tx <= 90:
                    metrics["moderately_active"] += 1
                else:
                    metrics["minimally_active"] += 1
        
        return metrics