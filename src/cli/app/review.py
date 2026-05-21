"""评审 CLI — 批量评审知识条目。

Usage:
    >>> from app.review import list_items, approve_item, reject_item
    >>> from app.reviewers.data import load_domains, load_reviews, save_reviews
    >>> import tempfile, json, os
    >>> from pathlib import Path
    >>> from app.config import settings
    >>> old = settings.data_home
    >>> tmp = Path(tempfile.mkdtemp())
    >>> settings.data_home = tmp
    >>> d = tmp / "test-domain"
    >>> d.mkdir()
    >>> (d / "domain.json").write_text('{"id":"test","name":"test"}')
    >>> (d / "ontologies.json").write_text('{"ontologies":[{"id":"o1","name":"onto1","label":"本体1"}]}')
    >>> (d / "instances.json").write_text('{"instances":[]}')
    >>> (d / "relations.json").write_text('{"relations":[]}')
    >>> domains = load_domains()
    >>> reviews = load_reviews()
    >>> items = list_items(domains, reviews)
    >>> len(items)
    1
    >>> items[0]["status"]
    '待评审'
    >>> approve_item("test-domain:ontology:o1", save=False)
    'test-domain:ontology:o1'
    >>> settings.data_home = old
    >>> import shutil; shutil.rmtree(tmp)
"""

from app.reviewers.data import (
    REVIEW_FILE,
    load_domains,
    load_reviews,
    save_reviews,
    get_review_status,
    set_review_status,
)


def list_items(domains=None, reviews=None, pending_only=False, domain_filter=None):
    """列出所有待审项。

    Args:
        domains: 领域列表，不传则加载
        reviews: 评审记录，不传则加载
        pending_only: 只显示待审项
        domain_filter: 按领域名过滤

    Returns:
        list[dict]: 每项包含 type / id / label / status / comment / key
    """
    if domains is None:
        domains = load_domains()
    if reviews is None:
        reviews = load_reviews()

    result = []
    for d in domains:
        if domain_filter and d["dir"] != domain_filter:
            continue

        for o in d["ontologies"]:
            key = f"{d['dir']}:ontology:{o['id']}"
            s, c = get_review_status(reviews, key)
            if pending_only and s != "待评审":
                continue
            result.append({
                "domain": d["dir"],
                "type": "ontology",
                "id": o["id"],
                "label": o.get("label", o.get("name", "")),
                "status": s,
                "comment": c,
                "key": key,
            })

        for inst in d["instances"]:
            key = f"{d['dir']}:instance:{inst['id']}"
            s, c = get_review_status(reviews, key)
            if pending_only and s != "待评审":
                continue
            result.append({
                "domain": d["dir"],
                "type": "instance",
                "id": inst["id"],
                "label": inst.get("subject", ""),
                "status": s,
                "comment": c,
                "key": key,
            })

        for r in d["relations"]:
            key = f"{d['dir']}:relation:{r['id']}"
            s, c = get_review_status(reviews, key)
            if pending_only and s != "待评审":
                continue
            result.append({
                "domain": d["dir"],
                "type": "relation",
                "id": r["id"],
                "label": r.get("relation", ""),
                "status": s,
                "comment": c,
                "key": key,
            })

    return result


def approve_item(key, comment="", save=True):
    """通过指定条目。

    Args:
        key: 条目 key（如 biz-ops:ontology:role-responsibility）
        comment: 备注
        save: 是否保存到文件

    Returns:
        str: 被通过的 key
    """
    reviews = load_reviews()
    set_review_status(reviews, key, "通过", comment)
    if save:
        save_reviews(reviews)
    return key


def approve_all(comment="", pending_only=True):
    """通过所有条目。

    Args:
        comment: 备注
        pending_only: 只通过待审项

    Returns:
        int: 通过的条目数
    """
    domains = load_domains()
    reviews = load_reviews()
    items = list_items(domains, reviews, pending_only=True)
    for item in items:
        set_review_status(reviews, item["key"], "通过", comment)
    save_reviews(reviews)
    return len(items)


def reject_item(key, reason="", save=True):
    """拒绝指定条目。

    Args:
        key: 条目 key
        reason: 拒绝原因
        save: 是否保存到文件

    Returns:
        str: 被拒绝的 key
    """
    reviews = load_reviews()
    set_review_status(reviews, key, "需修改", reason)
    if save:
        save_reviews(reviews)
    return key


def reset_reviews():
    """重置所有评审记录。"""
    if REVIEW_FILE.exists():
        REVIEW_FILE.unlink()
