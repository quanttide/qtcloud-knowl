mod acquire;
mod config;
mod extract_by_type;
mod kb_extract;
mod llm;
mod summary;

use clap::{Parser, Subcommand};

use config::Settings;

#[derive(Parser)]
#[command(name = "qtcloud-knowl", version, about = "Knowledge Agent CLI")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// 知识库抽取：从 .md 文档生成知识库 JSON（domain/ontologies/instances）
    Extract(kb_extract::KBExtractArgs),
    /// 知识获取：从文档提取规则并评估可编码性
    Acquire(acquire::AcquireArgs),
    /// 知识抽取：本体 YAML → 结构化产物
    ExtractByType(extract_by_type::ExtractByTypeArgs),
    /// 知识总结：忠实总结现有知识
    Summary(summary::SummaryArgs),
}

fn main() {
    let cli = Cli::parse();
    let settings = Settings::load();
    let result = match &cli.command {
        Commands::Extract(args) => kb_extract::run(args, &settings),
        Commands::Acquire(args) => acquire::run(args, &settings),
        Commands::ExtractByType(args) => extract_by_type::run(args, &settings),
        Commands::Summary(args) => summary::run(args, &settings),
    };
    if let Err(e) = result {
        eprintln!("错误: {:#}", e);
        std::process::exit(1);
    }
}
