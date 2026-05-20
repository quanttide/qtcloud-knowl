# TODO

## 已发布

v0.0.5 → v0.0.10 全部完成，见 [CHANGELOG.md](CHANGELOG.md)。

## v0.0.11 — 审计结果不可靠，环境变量配置不灵活

### P0 — 无效路径崩溃

- [ ] **#26** 不在 import 阶段崩溃，改为命令入口处校验路径
  - 停止条件：`QTCLOUD_KNOWL_DATA_HOME=/nonexistent` 不再报 `PermissionError`，而是输出"请确认数据目录路径"
  - 方案：将 `data_home` 的 `LocalStorage` 调用改为惰性求值，或在命令入口处拦截

### P1 — diff 跨模式污染

- [ ] **#27** diff 按审计模式（simple/full）隔离存储
  - 停止条件：先跑 `--mode full` 再跑 `--mode simple`，diff 不显示假阳性"已修复"
  - 方案：`audit.json` 中记录 mode，加载时只匹配同 mode 的状态

### P2 — env var 空串不 fallback

- [ ] **#28** env var 置空串时回退到默认值
  - 停止条件：`QTCLOUD_KNOWL_DATA_HOME=""` 等价于未设置，使用 `LocalStorage` 默认路径
  - 方案：Path 字段加 validator，空串视为 None

### P3 — init_domain 噪音

- [ ] **#29** verbose 模式也过滤 init_domain 内部日志
  - 停止条件：`extract --verbose` 不显示"领域 xxx 初始化完成"
  - 方案：init_domain 的打印改为通过回调/参数控制

### P4 — 细节打磨

- [ ] **#30** `audit --help` 中 `--mode` 括号风格统一
- [ ] **#31** detect-domain 隐藏命令的输出去掉技术分数，只留推荐结论

---

## v0.1.0 — 业务专家还不能自助完成全流程

（待启动：LLM 语义抽取 + audit 质量门禁 → 文档入库到发布的完整闭环）
