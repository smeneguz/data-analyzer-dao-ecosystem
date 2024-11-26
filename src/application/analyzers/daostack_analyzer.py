# src/application/analyzers/daostack_analyzer.py
from typing import Dict
import pandas as pd
from ...domain.interfaces.platform_analyzer import PlatformAnalyzer

class DAOstackAnalyzer(PlatformAnalyzer):
    def get_organization_stats(self, platform_files: Dict) -> Dict[str, int]:
        daos_df = pd.read_csv(platform_files['daos'])
        proposals_df = pd.read_csv(platform_files['proposals'])
        
        total_orgs = len(daos_df)
        
        # Consider a DAO active if it has proposals
        active_daos = len(set(proposals_df['dao'].unique()) & 
                         set(daos_df['dao'].unique()))
        
        return {
            "total_organizations": total_orgs,
            "active_organizations": active_daos,
            "inactive_organizations": total_orgs - active_daos
        }