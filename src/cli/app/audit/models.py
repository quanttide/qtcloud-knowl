from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class AuditMode(Enum):
    SIMPLE = "simple"
    FULL = "full"

    @classmethod
    def _missing_(cls, value):  # pragma: no cover
        if isinstance(value, str):
            for member in cls:
                if member.value == value:
                    return member
        return None


@dataclass(frozen=True)
class AuditIssue:
    category: str
    group: str
    label: str
    action: str = ""

    def issue_key(self) -> str:
        return f"{self.category}|{self.group}|{self.label}"


@dataclass(frozen=True)
class AuditDiff:
    fixed: frozenset
    new: frozenset
    pending: frozenset
    previous_timestamp: Optional[str] = None

    @classmethod
    def compute(cls, previous, current, prev_timestamp=None):
        prev_set = frozenset(i.issue_key() for i in previous)
        curr_set = frozenset(i.issue_key() for i in current)
        return cls(
            fixed=prev_set - curr_set,
            new=curr_set - prev_set,
            pending=prev_set & curr_set,
            previous_timestamp=prev_timestamp,
        )

    @property
    def has_changes(self) -> bool:
        return bool(self.fixed or self.new or self.pending)

    @property
    def is_identical(self) -> bool:
        return not self.has_changes


@dataclass
class AuditState:
    mode: AuditMode
    issues: list
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AuditReport:
    need_confirm: list
    auto_fixable: list
    suggestions: list
    mode: AuditMode
