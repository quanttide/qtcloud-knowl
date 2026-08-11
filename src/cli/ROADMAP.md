# ROADMAP

## v0.3.0（当前）— Rust 重构 + qtadmin knowl 合并

已完成：

- Python 实现整体重构为 Rust（PyPI 包名 `qtcloud-knowl-cli` 保留，命令 `qtcloud-knowl`）
- 合并 qtadmin knowl：`acquire`（规则提取 + 可编码性评估）、`extract-by-type`（7 类本体抽取）、`summary`（知识总结）
- `extract`（知识库抽取）行为对齐 Python 版：prompt 模板、字段清洗、UUID 化
- 命令集：`extract` / `acquire` / `extract-by-type` / `summary`
- 配置对齐：`QTCLOUD_KNOWL_*` 环境变量（兼容 `DEEPSEEK_API_KEY`）

待办：

- [ ] **PyPI 打包验证**：maturin（`bindings = "bin"`）构建 wheel，`pip install qtcloud-knowl-cli` 后 `qtcloud-knowl` 命令可用——**留待发布时测试**（本地 maturin 未装，配置已就位）
- [ ] Vault API key 支持（Python 版有 pydantic-vault，Rust 版暂为环境变量）

## v0.4.0（规划）— 信息→知识管道

承接原 v0.2.0 Python 设计愿景，以 Rust 实现：

- 输入抽象为 InformationSource 接口（文档 / 结构化数据 / 对话）
- 多阶段抽取管道：语境理解 → 概念抽取 → 结构建模 → 验证 → 入库
- KnowledgeItem 模型（`source_ref` 溯源）
- 多格式导出（`--format yaml / markdown`）
- 审计功能回归
