# src/application/analyzers/daohaus_analyzer.py
from typing import Dict
import pandas as pd
from ...domain.interfaces.platform_analyzer import PlatformAnalyzer

class DAOhausAnalyzer(PlatformAnalyzer):
    def get_organization_stats(self, platform_files: Dict) -> Dict[str, int]:
        moloches_df = pd.read_csv(platform_files['moloches'])
        proposals_df = pd.read_csv(platform_files['proposals'])
        
        total_orgs = len(moloches_df)
        
        # Consider a DAO active if it has proposals
        active_daos = len(set(proposals_df['molochAddress'].unique()) & 
                         set(moloches_df['molochAddress'].unique()))
        
        return {
            "total_organizations": total_orgs,
            "active_organizations": active_daos,
            "inactive_organizations": total_orgs - active_daos
        }