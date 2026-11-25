"""A single problem found during the review (a plain data structure)."""

from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass(frozen=True)
class Finding:
    category: str
    severity: Severity
    line: int
    message: str
