"""全量质量审计 — 串行执行全部检测，生成业务语言报告。"""
from app.audit.service import run
from app.audit.report import Report, ReportRepository
