# src/domain/entities/dao_activity.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class DAOActivityInfo:
    """Stores activity information for a single DAO."""
    address: str
    name: Optional[str]
    activity_level: str
    last_activity: datetime
    transaction_count: int = 0
    proposal_count: int = 0
    member_count: Optional[int] = None