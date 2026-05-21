---
name: devops-release
description: 发布 Git 仓库 Release。必须先写 CHANGELOG 再打 tag，禁止跳步。
---

# devops-release

> **⚠ 硬约束：不执行预检查 → 禁止发布**
> 加载此 Skill 后，必须按下方工作流从头到尾逐行执行命令。
> 标有"必须执行，不可跳过"的步骤是强制性的，AI 不得合并、跳过或提前执行后续步骤。

## 包结构

tcloud-knowl 包含两个可发布包：

| 包 | 路径 | tag 前缀 |
|----|------|---------|
| CLI | src/cli/ | cli/v |
| Python SDK | packages/python/ | python-sdk/v |

## 规则

- 版本号遵循 semver
- 必须先更新 CHANGELOG.md，提交推送，再执行发布
- 发布前确认工作区干净
- Release notes 只包含对应版本内容
- 发布前确认所有子模块引用是最新的

## 工作流

### 1. 选择发布包

设置变量：
```bash
PACKAGE=cli                    # 或 python-sdk
CHANGELOG_DIR=src/cli          # 或 packages/python
TAG_PREFIX=cli/v               # 或 python-sdk/v
```

### 2. 预检查

必须执行，不可跳过

```bash
git status

VERSION="v0.0.0"
if ! [[ "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?$ ]]; then
  echo "错误: 版本号格式错误"
  exit 1
fi

FULL_TAG="${TAG_PREFIX}${VERSION#v}"

if ! grep -q "^## \[${VERSION#v}\]" "${CHANGELOG_DIR}/CHANGELOG.md"; then
  echo "错误: ${CHANGELOG_DIR}/CHANGELOG.md 未找到 ${VERSION#v} 版本记录"
  exit 1
fi

NOTES=$(sed -n "/^## \[${VERSION#v}\]/,/^## \[/p" "${CHANGELOG_DIR}/CHANGELOG.md" | sed '1d;$d')
if [ -z "$NOTES" ]; then
  echo "错误: 无法提取版本内容"
  exit 1
fi

if git tag -l | grep -q "^${FULL_TAG}$"; then
  echo "错误: 标签 $FULL_TAG 已存在"
  exit 1
fi

cd ${CHANGELOG_DIR} && uv run pytest -q && cd -

echo "=== Release Notes 预览 ==="
echo "$NOTES"
echo "========================="
```

### 3. 发布前确认

```
发布版本: ${FULL_TAG}

检查结果:
✓ 版本号格式正确
✓ CHANGELOG.md 包含目标版本
✓ Release Notes 提取成功
✓ 标签不存在
✓ 工作区干净
✓ 测试通过

确认发布？(y/n)
```

### 4. 发布

```bash
git tag ${FULL_TAG}
git push origin ${FULL_TAG}

gh release create ${FULL_TAG} \
  --title "${FULL_TAG}" \
  --notes "$NOTES" \
  --repo quanttide/qtcloud-knowl

gh release view ${FULL_TAG} --repo quanttide/qtcloud-knowl
```

### 5. 更新主仓库

```bash
cd /path/to/quanttide-platform
git add apps/qtcloud-knowl
git commit -m "chore: update submodule qtcloud-knowl (${FULL_TAG})"
git push
```

### 6. 错误处理和回滚

```bash
git tag -d ${FULL_TAG}
git push origin --delete ${FULL_TAG} 2>/dev/null || true
gh release delete ${FULL_TAG} --repo quanttide/qtcloud-knowl --yes
```

## 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| CHANGELOG 缺少版本 | 忘记更新 | 添加版本记录后再发布 |
| 标签已存在 | 重复发布 | 删除旧标签或使用新版本号 |
| 工作区脏 | 有未提交变更 | 提交或暂存后再发布 |
| Release Notes 为空 | 版本格式不匹配 | 检查 CHANGELOG 版本标题格式 |

## 输出

### 成功时返回

```
✓ Release ${FULL_TAG} 创建成功
  标签: ${FULL_TAG}
  URL: https://github.com/quanttide/qtcloud-knowl/releases/tag/${FULL_TAG}
```

### 失败时返回

```
✗ Release ${FULL_TAG} 创建失败
  错误码: <ERROR_CODE>
  原因: <错误描述>
```