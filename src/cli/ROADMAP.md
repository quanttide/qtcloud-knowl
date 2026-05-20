# ROADMAP

## v0.0.4: 抽离文档源管理层，净化 `config.py`

### 背景

`config.py` 仍残留一条模块级 `SAMPLE_DIR`，指向原始源文档目录（`fixtures/input/`），仅被两个 validator 用作 CLI 默认值。这违反了"`config.py` 只含运行时配置"的原则——源文档路径是开发期结构，不应由配置层硬编码。

| 现状 | 问题 |
|------|------|
| `config.py` 导出 `SAMPLE_DIR` | 与 `settings.data_home` 混在同一模块，职责不清 |
| `fusion_check.py`、`find_undefined.py` 默认值依赖 `SAMPLE_DIR` | CLI 隐含了对夹具目录的耦合 |
| 源文档加载逻辑分散在两个 validator 内 | 无统一缓存、无统一接口 |

### 执行步骤

1. **创建 `app/sources/` 模块** — 统一负责源文档的定位、加载、缓存
   - `loader.py` — 按文件名或 glob 模式读取文档内容
   - `resolver.py` — 处理《引用》解析，维护文件→标题映射
   - 提供 `resolve_ref(title) → Path`、`load_source(name) → str` 等接口
2. **修改 `fusion_check.py`** — `check_broken_references` 改用 `sources.resolve_ref`，不再直接操作 `SAMPLE_DIR`
3. **修改 `find_undefined.py`** — 文档扫描改用 `sources.load_source`，不再直接操作 `SAMPLE_DIR`
4. **`--sample-dir` 改为必填参数** — 或由 `sources` 模块通过其他方式确定默认路径
5. **`config.py` 移除 `SAMPLE_DIR`** — 净化后只保留 `Settings.data_home`

### 验收标准

- `config.py` 不引用 `fixtures/` 路径
- `fusion_check.py` 和 `find_undefined.py` 不直接引用 `SAMPLE_DIR`
- `app/sources/` 可独立测试，不依赖 fixtures 目录存在
- 所有测试仍然通过

---

## v0.0.3: 使用 `quanttide.LocalStorage` 实现跨平台路径 ✅

已于 `d7a183a`、`ccee141`、`29248e4` 完成。
