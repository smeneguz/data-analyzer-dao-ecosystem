# src/application/services/dao_analyzer_service.py
from typing import Dict
import os
from ...domain.interfaces.dao_repository import DAORepository
from ..analyzers.aragon_analyzer import AragonAnalyzer
from ..analyzers.daohaus_analyzer import DAOhausAnalyzer
from ..analyzers.daostack_analyzer import DAOstackAnalyzer

class DAOAnalyzerService:
    """Service for analyzing DAO data across different platforms."""
    
    def __init__(self, dao_repository: DAORepository):
        self.dao_repository = dao_repository
        self.analyzers = {
            'aragon': AragonAnalyzer(),
            'daohaus': DAOhausAnalyzer(),
            'daostack': DAOstackAnalyzer()
        }
        
        # Required files for each platform
        self.required_files = {
            'aragon': [ 'organizations.csv', 'transactions.csv', 'votes.csv', 'tokenHolders.csv', 'apps.csv', 'casts.csv'],
            'daohaus': ['moloches.csv', 'proposals.csv', 'votes.csv', 'members.csv', 'rageQuits.csv'],
            'daostack': ['daos.csv', 'proposals.csv', 'votes.csv', 'stakes.csv', 'reputationHolders.csv']
        }

    def get_active_organizations(self, platform_name: str) -> Dict[str, int]:
        """
        Get organization statistics for a specific platform.
        
        Args:
            platform_name: Name of the platform to analyze
            
        Returns:
            Dictionary containing organization statistics
            
        Raises:
            ValueError: If platform or required files not found
            Exception: For other processing errors
        """
        platform_name = platform_name.lower()
        
        # Validate platform
        if platform_name not in self.analyzers:
            raise ValueError(f"Platform {platform_name} not supported")
            
        # Get platform data
        platforms = self.dao_repository.get_all_platforms()
        platform = next((p for p in platforms if p.name.lower() == platform_name), None)
        
        if not platform:
            raise ValueError(f"Platform {platform_name} not found in data")
            
        # Prepare file paths
        required_files = self.required_files[platform_name]
        platform_files = {}
        
        for file_name in required_files:
            file_path = os.path.join(self.dao_repository.base_path, platform_name, file_name)
            if not os.path.exists(file_path):
                raise ValueError(f"Required file not found: {file_name}")
            platform_files[file_name.split('.')[0]] = file_path
            
        # Get appropriate analyzer and process data
        analyzer = self.analyzers[platform_name]
        
        try:
            return analyzer.get_organization_stats(platform_files)
        except Exception as e:
            raise Exception(f"Error analyzing {platform_name} data: {str(e)}")
        
    

    def get_file_structure(self, platform_name: str = None) -> Dict:
        """
        Get detailed file and column information for platforms.
        
        Args:
            platform_name: Optional; specific platform to analyze. If None, shows all platforms.
            
        Returns:
            Dictionary containing file structures and column descriptions
        """
        platforms = self.dao_repository.get_all_platforms()
        
        if platform_name:
            platform_name = platform_name.lower()
            platform = next((p for p in platforms if p.name.lower() == platform_name), None)
            if not platform:
                raise ValueError(f"Platform {platform_name} not found")
            platforms = [platform]

        structure = {}
        for platform in platforms:
            platform_files = {}
            for file in platform.files:
                columns_info = {}
                for col in file.columns:
                    description = file.column_descriptions.get(col, "No description available")
                    sample_values = [str(record.get(col, '')) for record in file.sample_data[:3]]
                    columns_info[col] = {
                        'description': description,
                        'sample_values': sample_values
                    }
                
                platform_files[file.name] = {
                    'columns': columns_info,
                    'total_columns': len(file.columns),
                    'has_samples': bool(file.sample_data)
                }
            
            structure[platform.name] = platform_files
            
        return structure