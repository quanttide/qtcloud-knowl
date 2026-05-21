"""知识抽取 — 从源文档自动创建知识库骨架。"""

from collections import Counter
from pathlib import Path

from qtcloud_knowl.loader import load_all_domains

from app.config import settings

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"


def _load_prompt(name):
    path = PROMPT_DIR / name
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def extract_with_llm(document_path, prompt_name="ontology_discovery.txt"):
    """对文档运行 LLM 抽取，输出原始结果。

    Args:
        document_path: 文档文件路径
        prompt_name: prompt 模板文件名

    Returns:
        str: LLM 原始输出
    """
    from quanttide_agent import LLM

    doc_path = Path(document_path)
    if not doc_path.exists():
        return f"错误: 文件不存在 {doc_path}"

    prompt = _load_prompt(prompt_name)
    if not prompt:
        return f"错误: prompt 模板不存在 {prompt_name}"

    content = doc_path.read_text(encoding="utf-8")
    filled = prompt.replace("{document}", content)

    kwargs = {}
    if settings.llm_base_url:
        kwargs["base_url"] = settings.llm_base_url
    llm = LLM(model=settings.llm_model, api_key=settings.llm_api_key, **kwargs)
    response = llm.complete(filled)
    return response.content


def _describe(domain_hits, existing_domains):
    new = sum(1 for d in domain_hits if d not in existing_domains)
    total_files = sum(domain_hits.values())
    parts = []
    if new:
        parts.append(f"新增 {new} 个领域")
    if total_files:
        parts.append(f"共收录 {total_files} 份文档")
    return "，".join(parts) if parts else None


def run(source=None, data_dir=None, verbose=False):
    sdir = Path(source) if source else settings.sample_home
    ddir = Path(data_dir) if data_dir else settings.data_home

    import typer

    if not sdir:
        print("错误: 未设置源文档目录")
        print("请设置 QTCLOUD_KNOWL_SAMPLE_HOME 环境变量，或传入 --source 参数。")
        raise typer.Exit(code=1)
    if not sdir.exists():
        print(f"错误: 源文档目录不存在")
        print(f"  路径: {sdir}")
        print("请确认目录路径是否正确。")
        raise typer.Exit(code=1)

    md_files = list(sdir.glob("*.md"))

    if not md_files:
        ddir.mkdir(parents=True, exist_ok=True)
        print("没有 .md 文件需要处理，知识库骨架目录已就绪。")
        return 0

    ddir.mkdir(parents=True, exist_ok=True)

    domain_hits = Counter()
    file_domains = {}

    existing_domains = {}
    try:
        for d, domain, ontologies, instances, relations in load_all_domains(ddir):
            existing_domains[domain.id] = domain
    except Exception:
        pass

    for f in sorted(md_files):
        content = f.read_text(encoding="utf-8")
        best_domain = None
        best_score = 0

        for d, domain, ontologies, instances, relations in load_all_domains(ddir):
            if not domain.vocabulary:
                continue
            score = sum(content.count(term) for term in domain.vocabulary)
            if score > best_score:
                best_score = score
                best_domain = domain.id

        if best_domain:
            domain_hits[best_domain] += 1
            file_domains[f.name] = best_domain

    import io
    import sys

    from app.detectors.init_domain import run as init_domain_run

    for domain_id in sorted(
        set([d for d in domain_hits.keys()] + list(existing_domains.keys()))
    ):
        old, sys.stdout = sys.stdout, io.StringIO()
        try:
            init_domain_run(domain_id, data_dir=str(ddir))
        finally:
            sys.stdout = old

    summary = _describe(domain_hits, existing_domains)
    if summary:
        print(f"抽取完成。{summary}。骨架文件已保存到 {ddir}。")
    else:
        print(
            "抽取完成。未匹配到已有领域词汇表，可先配置 domain.json 中的 vocabulary 后再试。"
        )

    if verbose:
        print()
        if domain_hits:
            print("推荐领域:")
            for domain_id, count in domain_hits.most_common():
                tag = "（新建）" if domain_id not in existing_domains else "（已有）"
                print(f"  {domain_id}{tag}: {count} 个文件匹配")
            print()
            print("文件归属:")
            for fname, domain_id in sorted(file_domains.items()):
                print(f"  {fname} → {domain_id}")
        else:
            print("（未发现与已有领域匹配的文件）")

        if settings.llm_api_key:
            print()
            print(
                "LLM 已就绪，可执行语义抽取。运行 qtcloud-knowl audit 检查骨架完整性。"
            )
        else:
            print()
            print("提示: 设置 QTCLOUD_KNOWL_LLM_API_KEY 可启用语义抽取。")

    return 0
