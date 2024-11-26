# src/application/analyzers/aragon_analyzer.py
from typing import Dict
import pandas as pd
import os
from ...domain.interfaces.platform_analyzer import PlatformAnalyzer

class AragonAnalyzer(PlatformAnalyzer):
    def get_organization_stats(self, platform_files: Dict) -> Dict[str, int]:
        orgs_df = pd.read_csv(platform_files['organizations'])
        tx_df = pd.read_csv(platform_files['transactions'])
        
        total_orgs = len(orgs_df)
        active_orgs = len(set(tx_df['orgAddress'].unique()) & set(orgs_df['orgAddress'].unique()))
        
        return {
            "total_organizations": total_orgs,
            "active_organizations": active_orgs,
            "inactive_organizations": total_orgs - active_orgs
        }