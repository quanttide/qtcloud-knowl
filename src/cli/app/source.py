"""源文档管理 — 下载、列出、清理源文档。

Usage:
    >>> from app.source import download, list_sources, remove
    >>> import tempfile, os
    >>> from pathlib import Path
    >>> from app.config import settings
    >>> old = settings.sample_home
    >>> tmp = Path(tempfile.mkdtemp())
    >>> settings.sample_home = tmp
    >>> list_sources()
    []
    >>> settings.sample_home = old
    >>> import shutil; shutil.rmtree(tmp)
"""

from pathlib import Path

from app.config import settings


def _sources_dir():
    return settings.source_home


def _repo_name_from_url(url: str) -> str:
    """从 Git URL 提取仓库名。

    >>> _repo_name_from_url("https://github.com/user/repo.git")
    'repo'
    >>> _repo_name_from_url("git@github.com:user/repo.git")
    'repo'
    """
    name = url.rstrip("/").split("/")[-1]
    if name.endswith(".git"):
        name = name[:-4]
    return name


def list_sources():
    """列出已下载的源文档。"""
    src_dir = _sources_dir()
    if not src_dir.exists():
        return []
    return sorted(d.name for d in src_dir.iterdir() if d.is_dir())


def download(name=None, url=None):
    """下载源文档。

    Args:
        name: 本地目录名（不指定时从 URL 自动提取）
        url: Git 仓库 URL（download 时必填）

    Returns:
        str: 结果消息
    """
    import subprocess
    import sys

    if url is None:
        return "错误: 请指定 --url"

    if name is None:
        name = _repo_name_from_url(url)

    target = _sources_dir() / name
    if target.exists():
        return f"✓ {name} 已存在"

    target.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["git", "clone", "--depth", "1", url, str(target)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return f"错误: 下载失败\n{result.stderr.strip()}"
    return f"✓ {name} 已下载到 {target}"


def download_all():
    """下载所有源文档。

    Returns:
        list[str]: 每条下载结果
    """
    results = []
    for name in SOURCES:
        results.append(download(name))
    return results


def remove(name):
    """删除指定源文档。

    Args:
        name: 源文档名称

    Returns:
        str: 结果消息
    """
    target = _sources_dir() / name
    if not target.exists():
        return f"✗ {name} 不存在"
    import shutil

    shutil.rmtree(target)
    return f"✗ {name} 已删除"


def remove_all():
    """删除所有源文档。

    Returns:
        list[str]: 每条删除结果
    """
    results = []
    for name in list_sources():
        results.append(remove(name))
    return results
