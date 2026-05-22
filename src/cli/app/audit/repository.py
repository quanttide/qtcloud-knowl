import json
from pathlib import Path
from typing import Optional

from app.audit.models import AuditMode, AuditIssue, AuditState

AUDIT_STATE_FILE = "audit.json"


class AuditStateRepository:
    def __init__(self, state_home: Path):
        self._path = state_home / AUDIT_STATE_FILE

    def load(self, mode: Optional[AuditMode] = None) -> Optional[AuditState]:
        if not self._path.exists():
            return None
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            if mode and data.get("mode") != mode.value:
                return None
            issues = [
                AuditIssue(category=i["category"], group=i["group"], label=i["label"], action=i.get("action", ""))
                for i in data.get("issues", [])
            ]
            return AuditState(
                mode=AuditMode(data["mode"]),
                issues=issues,
                timestamp=data.get("timestamp", ""),
            )
        except Exception:
            return None

    def save(self, state: AuditState) -> None:
        data = {
            "timestamp": state.timestamp,
            "mode": state.mode.value,
            "issues": [
                {"category": i.category, "group": i.group, "label": i.label, "action": i.action}
                for i in state.issues
            ],
        }
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
