"""知识抽取 — 全程 LLM 驱动，从源文档直接生成知识库。"""

import json
from pathlib import Path

from app.config import settings

ALLOWED_FIELDS = ["id", "name", "label", "description"]


def _clean(item):
    """只保留 id/name/label/description 四个字段。"""
    return {k: item.get(k, "") for k in ALLOWED_FIELDS}


PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"


def _load_prompt(name):
    path = PROMPT_DIR / name
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def _save_knowledge_base(ddir, data):
    """将 LLM 返回的知识库结构写入文件。"""
    domain = data.get("domain", {})
    domain_id = domain.get("id", "default")

    domain_dir = ddir / domain_id
    domain_dir.mkdir(parents=True, exist_ok=True)

    with open(domain_dir / "domain.json", "w", encoding="utf-8") as f:
        json.dump(domain, f, ensure_ascii=False, indent=2)

    for key, filename in [
        ("ontologies", "ontologies.json"),
        ("instances", "instances.json"),
        ("relations", "relations.json"),
    ]:
        items = data.get(key, [])
        with open(domain_dir / filename, "w", encoding="utf-8") as f:
            json.dump({key: items}, f, ensure_ascii=False, indent=2)

    return domain_id


def _extract_dir(sdir, prompt_template="full_extraction.txt"):
    """对目录中所有 .md 文件执行 LLM 抽取，合并结果。"""
    from quanttide_agent import LLM

    prompt = _load_prompt(prompt_template)
    if not prompt:
        return f"错误: prompt 模板不存在 {prompt_template}"

    md_files = sorted(sdir.glob("*.md"))
    if not md_files:
        return "错误: 源目录中没有 .md 文件"

    if not settings.llm_api_key:
        return "错误: 未设置 LLM API Key（需通过环境变量 QTCLOUD_KNOWL_LLM_API_KEY 或 Vault 配置）"

    kwargs = {}
    if settings.llm_base_url:
        kwargs["base_url"] = settings.llm_base_url
    llm = LLM(model=settings.llm_model, api_key=settings.llm_api_key, **kwargs)

    all_domains = {}
    all_ontologies = {}
    all_instances = []
    all_relations = []

    for f in md_files:
        print(f"  [{f.name}] 正在抽取...", end=" ", flush=True)
        content = f.read_text(encoding="utf-8")
        filled = prompt.replace("{document}", content)

        response = llm.complete(filled)
        text = response.content.strip()

        if text.startswith("```"):
            text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        text = text.strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            print(f"⚠ 文件 {f.name} LLM 返回结果解析失败，跳过")
            continue

        print(
            f"✓ {len(data.get('ontologies', []))}本体/{len(data.get('instances', []))}实例"
        )

        domain = _clean(data.get("domain", {}))
        did = domain.get("id", f"from-{f.stem}")
        if did not in all_domains:
            all_domains[did] = domain

        for o in data.get("ontologies", []):
            o = _clean(o)
            oid = o.get("id", "")
            if oid and oid not in all_ontologies:
                all_ontologies[oid] = o

        for inst in data.get("instances", []):
            inst = _clean(inst)
            all_instances.append(inst)

        for r in data.get("relations", []):
            r = _clean(r)
            all_relations.append(r)

    return all_domains, list(all_ontologies.values()), all_instances, all_relations


def run(source=None, data_dir=None, verbose=False):
    sdir = Path(source) if source else None
    ddir = Path(data_dir) if data_dir else settings.data_home

    import typer

    if not sdir:
        print("错误: 请指定 --source")
        raise typer.Exit(code=1)
    if not sdir.exists():
        print(f"错误: 源文档目录不存在: {sdir}")
        raise typer.Exit(code=1)

    result = _extract_dir(sdir)
    if isinstance(result, str):
        print(result)
        return 1

    all_domains, all_ontologies, all_instances, all_relations = result

    ddir.mkdir(parents=True, exist_ok=True)

    domain_count = 0
    for domain in all_domains.values():
        did = domain.get("id", "")
        if not did:
            continue
        domain_dir = ddir / did
        domain_dir.mkdir(parents=True, exist_ok=True)

        with open(domain_dir / "domain.json", "w", encoding="utf-8") as f:
            json.dump(domain, f, ensure_ascii=False, indent=2)

        domain_ontologies = [
            o
            for o in all_ontologies
            if o.get("perspective") in (domain.get("perspective"), "") or True
        ]
        with open(domain_dir / "ontologies.json", "w", encoding="utf-8") as f:
            json.dump({"ontologies": all_ontologies}, f, ensure_ascii=False, indent=2)

        with open(domain_dir / "instances.json", "w", encoding="utf-8") as f:
            json.dump({"instances": all_instances}, f, ensure_ascii=False, indent=2)

        with open(domain_dir / "relations.json", "w", encoding="utf-8") as f:
            json.dump({"relations": all_relations}, f, ensure_ascii=False, indent=2)

        domain_count += 1

    print(f"抽取完成。生成 {domain_count} 个领域知识库，保存至 {ddir}。")
    if verbose:
        print(f"  本体: {len(all_ontologies)} 项")
        print(f"  实例: {len(all_instances)} 项")
        print(f"  关系: {len(all_relations)} 项")

    return 0
