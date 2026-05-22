"""Audit command implementation using quanttide-audit and quanttide-knowl."""

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from quanttide_audit.models import AuditCriteria, AuditFinding, AuditReport, AuditSeverity
from quanttide_knowl.models import Domain


def _load_domains(data_dir: Path) -> list[Domain]:
    if not data_dir.exists():
        return []
    domains: list[Domain] = []
    for entry in sorted(data_dir.iterdir()):
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        domain_path = entry / "domain.json"
        if not domain_path.exists():
            continue
        domain = Domain.model_validate_json(domain_path.read_text(encoding="utf-8"))
        domains.append(domain)
    return domains


def _check_missing_domains(domains: list[Domain], data_dir: Path) -> list[AuditFinding]:
    findings: list[AuditFinding] = []
    now = datetime.now(timezone.utc)
    if not domains:
        criterion = AuditCriteria(
            id=uuid4(),
            name="domain-exists",
            title="领域完整性检查",
            description="知识库中至少应包含一个领域",
            created_at=now,
            updated_at=now,
        )
        findings.append(
            AuditFinding(
                id=uuid4(),
                name="no-domains",
                title="知识库为空",
                criterion=criterion,
                severity=AuditSeverity.MAJOR,
                description=f"数据目录 {data_dir} 中没有找到任何领域",
                created_at=now,
                updated_at=now,
            )
        )
    return findings


def run(data_dir: str) -> int:
    ddir = Path(data_dir)
    domains = _load_domains(ddir)
    findings: list[AuditFinding] = []
    findings.extend(_check_missing_domains(domains, ddir))

    now = datetime.now(timezone.utc)
    report = AuditReport(
        id=uuid4(),
        name="knowledge-base-audit",
        title="知识库审计报告",
        description=f"数据目录: {ddir}",
        findings=findings,
        created_at=now,
        updated_at=now,
    )

    print(f"审计完成: {len(report.findings)} 个发现")
    for f in report.findings:
        print(f"  [{f.severity.value}] {f.title}")

    return 1 if findings else 0
