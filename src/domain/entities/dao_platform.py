# src/domain/entities/dao_platform.py
from dataclasses import dataclass
from typing import List
from .dao_file import DAOFile

@dataclass
class DAOPlatform:
    name: str
    files: List[DAOFile]