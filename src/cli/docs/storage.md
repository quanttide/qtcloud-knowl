# 数据存储方案

## 数据在哪

`qtcloud-knowl-cli` 将领域数据存储在操作系统的**用户数据目录**下，以 `quanttide/` 为产品统一命名空间隔离。

| 平台 | 默认路径 |
|------|---------|
| Linux | `~/.local/share/quanttide/qtcloud-knowl/` |
| macOS | `~/Library/Application Support/quanttide/qtcloud-knowl/` |
| Windows | `%APPDATA%/quanttide/qtcloud-knowl/` |

选择操作系统标准数据目录而非自定义路径（如 `~/.qtcloud-knowl/`），遵循三个原则：

1. **用户不需要记忆** —— 操作系统的标准目录是所有应用都遵循的约定，用户知道数据在哪、如何备份、什么能清什么不能清。
2. **工具自动覆盖** —— 定时备份脚本或备份软件已经覆盖了这些标准目录，新装的应用自然被包含。
3. **环境变量统一覆写** —— 如果确实需要自定义，用对应操作系统的标准覆盖变量即可。

选择 `quanttide/` 作为统一命名空间而非平铺到根目录，因为平台有多个子系统（`qtcloud-knowl`、`qtcloud-write`、`qtcloud-think`……），层级结构让用户一眼看出它们属于同一产品体系，备份时也只需一个命令覆盖整个 `quanttide/` 目录。

## 目录结构

```
~/.local/share/quanttide/qtcloud-knowl/
  biz-ops/
    domain.json         # 领域元信息（id、名称、词汇表）
    ontologies.json     # 本体定义列表
    instances.json      # 实例列表
    relations.json      # 跨领域关系列表
  doc-std/
    ...
  hr/
    ...
  org-gov/
    ...
```

## 覆盖默认路径

设置环境变量 `KNOWL_DATA_DIR` 可指向任意目录：

```bash
export KNOWL_DATA_DIR=~/my-knowledge-base
kcli summary
```

环境变量的优先级高于操作系统默认路径，不会修改 `~/.local/share/quanttide/qtcloud-knowl/`。

## 应用数据与测试数据

`src/cli/tests/fixtures/` 下包含一套完整的测试夹具数据，结构与应用数据一致。安装后的生产数据存放在用户数据目录，两者不冲突。

## 为什么不是数据库

CLI 工具的操作模式是"读 JSON → 分析 → 输出报告"：

- 单机运行，无并发写
- 数据量小（四个领域，每个一篇空文档的建模量）
- 用户需要直接用编辑器查看和修改 JSON

这三种约束下，文件系统 + JSON 比数据库更透明：用户可以用 `cat`、`grep`、`tree` 直接查看数据，不需要连接数据库客户端。
