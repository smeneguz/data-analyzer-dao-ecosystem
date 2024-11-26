# src/domain/interfaces/platform_analyzer.py
from abc import ABC, abstractmethod
from typing import Dict

class PlatformAnalyzer(ABC):
    """Interface for platform-specific analysis implementations."""
    
    @abstractmethod
    def get_organization_stats(self, platform_files: Dict) -> Dict[str, int]:
        """Calculate organization statistics for a specific platform."""
        pass