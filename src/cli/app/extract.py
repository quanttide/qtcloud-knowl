"""知识抽取 — 全程 LLM 驱动，从单篇文档生成知识库 JSON。"""

import json
import uuid
from pathlib import Path

from app.config import settings

ALLOWED_FIELDS = ["id", "name", "label", "description"]
ALLOWED_INSTANCE_FIELDS = ["id", "name", "label", "description", "ontology"]


def _make_uuid(name: str) -> str:
    return str(uuid.uuid4())


def _clean(item, is_instance=False):
    """只保留允许的字段，id 转为 UUID。
    返回 (uuid_cleaned, original_id) 元组。
    """
    original_id = item.get("id", "") or item.get("name", "unknown")
    fields = ALLOWED_INSTANCE_FIELDS if is_instance else ALLOWED_FIELDS
    cleaned = {k: item.get(k, "") for k in fields}
    cleaned["id"] = _make_uuid(original_id)
    return cleaned, original_id


PROMPT_DIR = Path(__file__).resolve().parent.parent / "assets" / "prompts"


def _load_prompt(name):
    path = PROMPT_DIR / name
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    return text.strip()


def extract(source: str, prompt_template: str = "extract.txt") -> dict:
    """从单个 .md 文件抽取知识，返回 {domain, ontologies, instances}。"""
    source_path = Path(source)

    if not source_path.exists():
        return {"error": f"文件不存在: {source}"}
    if source_path.suffix != ".md":
        return {"error": f"仅支持 .md 文件: {source}"}

    prompt_template_raw = _load_prompt(prompt_template)
    if not prompt_template_raw:
        return {"error": f"prompt 模板不存在: {prompt_template}"}

    if not settings.llm_api_key:
        return {"error": "未设置 LLM API Key（需通过环境变量 QTCLOUD_KNOWL_LLM_API_KEY 或 Vault 配置）"}

    prompt = prompt_template_raw.replace("{directory_name}", source_path.stem)

    document = source_path.read_text(encoding="utf-8")
    filled = prompt.replace("{document}", document)

    from quanttide_agent import LLM
    kwargs = {}
    if settings.llm_base_url:
        kwargs["base_url"] = settings.llm_base_url
    llm = LLM(model=settings.llm_model, api_key=settings.llm_api_key, **kwargs)

    response = llm.complete(filled)
    text = _strip_fences(response.content)

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {"error": f"LLM 返回结果解析失败: {text[:200]}"}

    result = {"domain": None, "ontologies": [], "instances": []}

    domain, _ = _clean(data.get("domain", {}))
    result["domain"] = domain

    for o in data.get("ontologies", []):
        o, _ = _clean(o)
        if o.get("id"):
            result["ontologies"].append(o)

    for inst in data.get("instances", []):
        inst, _ = _clean(inst, is_instance=True)
        result["instances"].append(inst)

    return result


def run(source=None, data_dir=None, verbose=False):
    sdir = Path(source) if source else None
    ddir = Path(data_dir) if data_dir else settings.data_home

    import typer

    if not sdir:
        print("错误: 请指定 --source")
        raise typer.Exit(code=1)

    if sdir.is_file():
        result = extract(str(sdir))
        if "error" in result:
            print(result["error"])
            raise typer.Exit(code=1)

        ddir.mkdir(parents=True, exist_ok=True)
        out_path = ddir / f"{sdir.stem}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"抽取完成。保存至 {out_path}。")
        return 0

    if not sdir.exists():
        print(f"错误: 源文档目录不存在: {sdir}")
        raise typer.Exit(code=1)

    md_files = sorted(sdir.glob("*.md"))
    if not md_files:
        print("错误: 源目录中没有 .md 文件")
        raise typer.Exit(code=1)

    ddir.mkdir(parents=True, exist_ok=True)

    all_domains = {}
    all_ontologies = {}
    all_instances = []

    for f in md_files:
        print(f"  [{f.name}] 正在抽取...", end=" ", flush=True)
        result = extract(str(f))
        if "error" in result:
            print(f"⚠ {result['error']}")
            continue

        domain = result["domain"]
        did = domain.get("id", "")
        if did and did not in all_domains:
            all_domains[did] = domain

        for o in result["ontologies"]:
            oid = o.get("id", "")
            if oid and oid not in all_ontologies:
                all_ontologies[oid] = o

        for inst in result["instances"]:
            all_instances.append(inst)

        print(f"✓ {len(result['ontologies'])}本体/{len(result['instances'])}实例")

    domain_count = 0
    for did, domain in all_domains.items():
        if not did:
            continue
        domain_dir = ddir / did
        domain_dir.mkdir(parents=True, exist_ok=True)

        with open(domain_dir / "domain.json", "w", encoding="utf-8") as f:
            json.dump(domain, f, ensure_ascii=False, indent=2)
        with open(domain_dir / "ontologies.json", "w", encoding="utf-8") as f:
            json.dump({"ontologies": list(all_ontologies.values())}, f, ensure_ascii=False, indent=2)
        with open(domain_dir / "instances.json", "w", encoding="utf-8") as f:
            json.dump({"instances": all_instances}, f, ensure_ascii=False, indent=2)

        domain_count += 1

    print(f"抽取完成。生成 {domain_count} 个领域知识库，保存至 {ddir}。")
    if verbose:
        print(f"  本体: {len(all_ontologies)} 项")
        print(f"  实例: {len(all_instances)} 项")

    return 0
