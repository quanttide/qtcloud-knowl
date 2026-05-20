# ROADMAP

## v0.0.4: CLI 重设计 — 统一配置层、typer 替换 ✅

### 变更

| 之前 | 之后 |
|------|------|
| `sys.argv` 手动分发 | `typer`，自动 `--help` / `--show-completion` |
| `find-undefined-terms <sample_dir> [data_dir]` | `find-undefined-terms`，从 `settings` 读路径 |
| `fusion-check [data_dir] [sample_dir]` | `fusion-check`，从 `settings` 读路径 |
| `SAMPLE_DIR` 模块级常量 | `Settings.sample_home`（`QTCLOUD_KNOWL_SAMPLE_HOME`） |
| `config.py` 含模块级路径常量 | `config.py` 只保留 `Settings` 类 |
| 无文档测试 | 文档测试覆盖 CLI help、storage.md env var、doctest 2 处 |

### 验收结果

- ✅ CLI 命令不接受 `data_dir` / `sample_dir` 位置参数
- ✅ `config.py` 不含模块级路径常量
- ✅ 42/42 测试通过（含文档测试、doctest）

### 未纳入（v0.0.4 阶段否决）

- **合并校验命令** — `find-undefined-terms`、`fusion-check`、`check-abstraction` 保持独立命令，不压入 `validate` 的 flag

---

## v0.0.3: 使用 `quanttide.LocalStorage` 实现跨平台路径 ✅

已于 `d7a183a`、`ccee141`、`29248e4` 完成。
