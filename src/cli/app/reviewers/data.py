import json
from pathlib import Path
from datetime import datetime
from app.config import settings
from qtcloud_knowl.loader import load_all_domains as _load_all

REVIEW_FILE = settings.data_home / ".review.json"


def _flatten(data: dict) -> dict:
    extra = data.pop("data", {})
    data.update(extra)
    return data


def load_domains():
    domains = []
    for d, domain, ontologies, instances, relations in _load_all(settings.data_home):
        domains.append({
            "dir": d.name,
            "info": domain.model_dump(),
            "ontologies": [o.model_dump() for o in ontologies],
            "instances": [_flatten(i.model_dump()) for i in instances],
            "relations": [r.model_dump() for r in relations],
        })
    return domains


def load_reviews():
    if REVIEW_FILE.exists():
        with open(REVIEW_FILE) as f:
            return json.load(f)
    return {}


def save_reviews(reviews):
    REVIEW_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REVIEW_FILE, "w") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)


def get_review_status(reviews, key):
    r = reviews.get(key, {})
    return r.get("status", "待评审"), r.get("comment", "")


def set_review_status(reviews, key, status, comment=""):
    reviews[key] = {"status": status, "comment": comment, "updated": datetime.now().isoformat()}
