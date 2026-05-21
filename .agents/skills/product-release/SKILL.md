---
name: product-release
description: 发布 qtcloud-knowl GitHub Release。子组件（CLI、SDK）各自发布，主仓库在子组件进展到一定程度后同步版本。
---

# Product Release

qtcloud-knowl 是一个多包仓库。发布分两个层级：

| 层级 | 标签 | 触发条件 | CHANGELOG |
|------|------|---------|-----------|
| **子组件** | `cli/v0.0.x`、`python-sdk/v0.0.x` | 每个 ROADMAP 版本完成 | 各子包目录下的 CHANGELOG.md |
| **主仓库** | `v0.0.x` | 子组件累积到足够进展 | 仓库根目录 CHANGELOG.md |

## 子组件发布

每个 ROADMAP 版本完成后发布对应子组件标签。

```bash
# 预检查
git status
git tag -l | grep "^<prefix>/v0\.0\.x$" && echo "标签已存在" || echo "标签可用"
grep -q "^## \[0\.0\.x\]" <子包 CHANGELOG.md> && echo "CHANGELOG 已更新" || echo "CHANGELOG 缺少版本"

# 发布
git tag <prefix>/v0.0.x
git push origin <prefix>/v0.0.x
gh release create <prefix>/v0.0.x --title "<prefix>/v0.0.x" --notes "$(sed -n '/^## \[0\.0\.x\]/,/^## \[/p' <子包 CHANGELOG.md> | sed '1d;$d')"
```

子组件发布不等主仓库版本——独立进行。

## 主仓库发布

主仓库版本（`v0.0.x`）在以下条件满足时发布：

1. 多个子组件版本已发布
2. 组件间接口已对齐（SDK 模型被 CLI 正常使用）
3. 整体 ROADMAP 阶段有实质推进

```bash
git tag v0.0.x
git push origin v0.0.x
gh release create v0.0.x --title "v0.0.x" --notes "$(sed -n '/^## \[0\.0\.x\]/,/^## \[/p' CHANGELOG.md | sed '1d;$d')"
```

主仓库 CHANGELOG.md 位于仓库根目录，记录跨组件的综合变更（目前不存在，首次发布前创建）。
