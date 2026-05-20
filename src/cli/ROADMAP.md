# ROADMAP

## v0.0.4: CLI 重设计 — 统一配置入口与验证命令

### 背景

CLI 当前的问题不在代码实现，而在接口设计暴露了内部实现细节：

1. **`sample_dir` 泄漏到 CLI 参数** — `find-undefined-terms` 和 `fusion-check` 各自接受源文档路径作为位置参数，本质是配置项被伪装成命令参数
2. **校验命令碎片化** — `validate`（JSON 结构）、`find-undefined-terms`（术语覆盖）、`fusion-check`（跨域一致性）、`check-abstraction`（抽象度）四个命令全是校验，被人为拆散
3. **数据源没有统一配置层** — `data_home` 已纳入 `Settings`（env var），`sample_home` 仍是模块级常量，两个配置层概念不一致

### 设计方案

| 现在 | 改进 |
|------|------|
| `find-undefined-terms <sample_dir> [data_dir]` | `validate --undefined`，从 `Settings` 读路径 |
| `fusion-check [data_dir] [sample_dir]` | `validate --fusion`，从 `Settings` 读路径 |
| `check-abstraction` | `validate --abstraction` |
| `SAMPLE_DIR` 模块级常量 | `Settings.sample_home`（`QTCLOUD_KNOWL_SAMPLE_HOME`） |

### 执行步骤

1. **`Settings` 新增 `sample_home`** — 环境变量 `QTCLOUD_KNOWL_SAMPLE_HOME`，fallback 无默认值（用户必须设置才能使用依赖源文档的功能）
2. **合并校验命令** — 将 `find-undefined-terms`、`fusion-check`、`check-abstraction` 作为 `validate` 的子开关
3. **清理 CLI 参数** — 去掉所有透传的 `data_dir`、`sample_dir` 位置参数，统一从 `settings` 读取
4. **移除 `SAMPLE_DIR`** — `config.py` 只保留 `Settings`

### 验收标准

- `validate` 是唯一的校验入口，子功能通过 `--undefined`、`--fusion`、`--abstraction` 访问
- CLI 命令不接受 `data_dir` 或 `sample_dir` 位置参数
- `config.py` 不含模块级路径常量
- 所有测试通过

---

## v0.0.3: 使用 `quanttide.LocalStorage` 实现跨平台路径 ✅

已于 `d7a183a`、`ccee141`、`29248e4` 完成。
