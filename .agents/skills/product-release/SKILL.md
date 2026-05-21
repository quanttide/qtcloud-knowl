---
name: product-release
description: 发布 qtcloud-knowl GitHub Release。支持 CLI 和 SDK 两种标签前缀，从对应 CHANGELOG 提取 Release Notes。
---

# Product Release

发布 Git 标签并创建 GitHub Release。

## 标签命名

| 组件 | 前缀 | CHANGELOG 位置 |
|------|------|---------------|
| CLI | `cli/v0.0.x` | `src/cli/CHANGELOG.md` |
| Python SDK | `python-sdk/v0.0.x` | `packages/python/CHANGELOG.md` |

## 预检查

```bash
# 工作区干净
git status

# 标签不存在
git tag -l | grep "^<prefix>/v0\.0\.x$" && echo "标签已存在" || echo "标签可用"

# CHANGELOG 包含版本
grep -q "^## \[0\.0\.x\]" <CHANGELOG.md> && echo "CHANGELOG 已更新" || echo "CHANGELOG 缺少版本"
```

## 发布

```bash
git tag <prefix>/v0.0.x
git push origin <prefix>/v0.0.x
gh release create <prefix>/v0.0.x --title "<prefix>/v0.0.x" --notes "$(sed -n '/^## \[0\.0\.x\]/,/^## \[/p' <CHANGELOG.md> | sed '1d;$d')"
```

## 验证

```bash
gh release view <prefix>/v0.0.x
```
