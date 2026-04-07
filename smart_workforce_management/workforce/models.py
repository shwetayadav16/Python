from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Employee:
    name: str
    department: str
    role: str
    salary: float
    experience_years: float
    performance_score: float
    attendance_rate: float
    id: Optional[int] = None
