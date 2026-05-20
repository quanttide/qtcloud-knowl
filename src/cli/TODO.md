# TODO

## 已发布

v0.0.5 → v0.0.10 全部完成，见 [CHANGELOG.md](CHANGELOG.md)。

## v0.0.11 — 审计结果不可靠，环境变量配置不灵活

✅ **#26** 无效路径不再崩溃 — `default_factory` 替代类级 LocalStorage 调用
✅ **#27** diff 按 mode 隔离 — `_load_audit_state(mode=mode)` 仅匹配同 mode 状态
✅ **#28** env var 空串回退 — `model_validator` 空串→None→默认值
✅ **#29** init_domain 噪音 — verbose 模式也抑制 init_domain 日志
✅ **#30** help 括号统一 — `simple（快速检查）/ full（全面审计）`
✅ **#31** detect-domain 去技术分数 — 只输出推荐领域名

---

## v0.1.0 — 业务专家还不能自助完成全流程

（待启动：LLM 语义抽取 + audit 质量门禁 → 文档入库到发布的完整闭环）
