# src/domain/entities/dao_file.py
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class DAOFile:
    name: str
    folder: str
    columns: List[str]
    column_descriptions: Dict[str, str]
    sample_data: List[Dict[str, Any]]