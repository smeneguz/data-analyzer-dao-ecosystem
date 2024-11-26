# src/domain/interfaces/dao_repository.py
from abc import ABC, abstractmethod
from typing import List
from ..entities.dao_platform import DAOPlatform

class DAORepository(ABC):
    @abstractmethod
    def get_all_platforms(self) -> List[DAOPlatform]:
        pass