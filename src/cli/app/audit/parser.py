import re
from typing import Optional

from app.audit.models import AuditIssue

MISS_TAG = "[MISS] "
FAIL_TAG = "[FAIL] "
DETECTED_TAG = "[检测到] "
NEED_CONFIRM_TAG = "需人确认"
TERM_USED_PATTERN = "使用了术语"
SECTION_HEADER_RE = re.compile(r"^=== (.+) ===")


def _parse_miss(line, current_domain, data_dir):
    if MISS_TAG not in line:
        return None
    fname = line.split(MISS_TAG, 1)[-1].strip()
    label = f"• 缺少文件 {fname}"
    if current_domain:
        action = f"运行 qtcloud-knowl auto-fix 自动补全，或创建文件 {data_dir}/{current_domain}/{fname}"
    else:
        action = "运行 qtcloud-knowl auto-fix 自动补全缺失文件"
    return AuditIssue(category="auto_fixable", group="文件结构问题", label=label, action=action)


def _parse_fail(line, current_domain, data_dir):
    if FAIL_TAG not in line:
        return None
    detail = line.split(FAIL_TAG, 1)[-1].strip()
    label = f"• JSON 格式错误: {detail}"
    action = (
        f"修复 {data_dir}/{current_domain}/ 下对应的 JSON 文件"
        if current_domain
        else "修复对应 JSON 文件格式"
    )
    return AuditIssue(category="auto_fixable", group="文件结构问题", label=label, action=action)


def _parse_term(line, _current_domain=None, _data_dir=None):
    if TERM_USED_PATTERN not in line:
        return None
    label = f"• {line}"
    action = "在对应领域 domain.json 的 vocabulary 字段中补充该术语"
    return AuditIssue(category="need_confirm", group="未定义术语", label=label, action=action)


def _parse_confirm(line, _current_domain=None, _data_dir=None):
    if NEED_CONFIRM_TAG not in line:
        return None
    label = line.replace(f"【{NEED_CONFIRM_TAG}】", "").strip()
    action = "确认该引用是否必要，如必要则补充源文件或删除引用"
    return AuditIssue(category="need_confirm", group="名称冲突或引用断裂", label=f"• {label}", action=action)


def _parse_abstraction(line, current_domain, data_dir):
    if DETECTED_TAG not in line:
        return None
    label = line.split(DETECTED_TAG, 1)[-1].strip()
    dest = (
        f"{data_dir}/{current_domain}/ontologies.json"
        if current_domain
        else "对应 ontologies.json"
    )
    action = f"重构 {dest} 中的 pattern，将具体值改为变量"
    return AuditIssue(category="suggestions", group="本体抽象度不足", label=f"• {label}", action=action)


_PARSERS = [
    _parse_miss,
    _parse_fail,
    _parse_term,
    _parse_confirm,
    _parse_abstraction,
]


class ToolOutputParser:
    def parse(self, output: str, data_dir: Optional[str] = None) -> list:
        issues = []
        current_domain = None
        for line in output.split("\n"):
            stripped = line.strip()
            if not stripped:
                continue
            m = SECTION_HEADER_RE.match(stripped)
            if m:
                current_domain = m.group(1)
                continue
            for parser in _PARSERS:
                result = parser(stripped, current_domain, data_dir)
                if result:
                    issues.append(result)
                    break
        return issues

    def has_issue(self, output: str) -> bool:
        return any(tag in output for tag in [MISS_TAG, FAIL_TAG, DETECTED_TAG, TERM_USED_PATTERN, NEED_CONFIRM_TAG])
