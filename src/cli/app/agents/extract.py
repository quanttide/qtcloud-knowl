"""知识抽取 — 从源文档自动创建知识库骨架。"""

from pathlib import Path
from collections import Counter
from app.config import settings
from app.loader import load_all_domains


def run(sample_dir=None, data_dir=None):
    sdir = Path(sample_dir) if sample_dir else settings.sample_home
    ddir = Path(data_dir) if data_dir else settings.data_home

    import typer
    if not sdir or not sdir.exists():
        print("错误: 源文档目录不存在或未设置")
        raise typer.Exit(code=1)

    md_files = list(sdir.glob("*.md"))
    print(f"源文档目录: {sdir}")
    print(f"目标目录: {ddir}")
    print(f"找到 {len(md_files)} 个源文件")
    print()

    if not md_files:
        ddir.mkdir(parents=True, exist_ok=True)
        print("没有 .md 文件需要处理。知识库骨架目录已就绪。")
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

    from app.detectors.init_domain import run as init_domain_run

    for domain_id in sorted(set([d for d in domain_hits.keys()] + list(existing_domains.keys()))):
        init_domain_run(domain_id, data_dir=str(ddir))

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
        print("（未发现与已有领域匹配的文件，可先配置领域词汇表再运行）")

    if settings.llm_api_key:
        print()
        print("LLM 已就绪，可执行语义抽取。运行方式：qtcloud-knowl audit 检查当前骨架完整性")
    else:
        print()
        print("提示: 设置 QTCLOUD_KNOWL_LLM_API_KEY 可启用语义抽取（推荐本体/实例/关系）")

    print()
    print(f"抽取完成。知识库位于: {ddir}")
    return 0
