//! 知识获取：从文档提取规则并评估可编码性。

use anyhow::Result;
use std::fs;
use std::path::PathBuf;

use crate::config::Settings;
use crate::llm::complete_json;

const SYSTEM_PROMPT: &str = r#"你是一个知识提取工具。从原始文档中提取业务规则并评估其可编码性。

输出 JSON，包含：
1. rules: 逐条规则（name, source, score, reason），score 为 1-5
2. rate: 可编码率（≥4分的规则占比）
3. ambiguities: 文档中的模糊点（category, description）
4. issues: 影响编码的具体问题（title, source, problem, suggestion）
5. observations: 值得记录的分析观察

评分标准：5=直接可编码，4=微调后可编码，3=需补充信息，2=模糊需重写，1=无法编码"#;

#[derive(clap::Args)]
pub struct AcquireArgs {
    /// 输入文件路径
    #[arg(long, default_value = "")]
    pub input: String,
    /// 输出目录
    #[arg(long, default_value = "data")]
    pub output: String,
}

fn default_sources() -> Vec<(String, PathBuf)> {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let assets = root.join("assets").join("business");
    vec![
        ("bylaw".into(), assets.join("bylaw.md")),
        ("handbook".into(), assets.join("handbook.md")),
        ("tutorial".into(), assets.join("tutorial.md")),
        ("profile".into(), assets.join("profile").join("index.md")),
    ]
}

fn read_text(path: &PathBuf) -> String {
    fs::read_to_string(path).unwrap_or_default()
}

/// 调用 LLM 从文本中提取知识（JSON），供 CLI 与示例复用。
pub fn extract_from_text(
    text: &str,
    system_prompt: &str,
    settings: &Settings,
) -> Result<serde_json::Value> {
    complete_json(
        settings,
        system_prompt,
        &format!("从以下原始文档中提取知识：\n\n{}", text),
    )
}

pub fn run(args: &AcquireArgs, settings: &Settings) -> Result<()> {
    let combined = if args.input.is_empty() {
        let mut text = String::new();
        for (name, path) in default_sources() {
            text.push_str(&format!("=== {} ===\n{}\n\n", name, read_text(&path)));
        }
        text
    } else {
        read_text(&PathBuf::from(&args.input))
    };

    println!("共 {} 字符", combined.len());

    let content = extract_from_text(&combined, SYSTEM_PROMPT, settings)?;

    let output_dir = PathBuf::from(&args.output);
    fs::create_dir_all(&output_dir)?;
    let yaml = serde_yaml::to_string(&content)?;
    fs::write(output_dir.join("extracted.yaml"), &yaml)?;

    let rules = content["rules"].as_array().map(|a| a.len()).unwrap_or(0);
    let rate = content["rate"].as_f64().unwrap_or(0.0);
    let ambiguities = content["ambiguities"]
        .as_array()
        .map(|a| a.len())
        .unwrap_or(0);
    let issues = content["issues"].as_array().map(|a| a.len()).unwrap_or(0);

    println!("规则数: {}", rules);
    println!("可编码率: {:.0}%", rate * 100.0);
    println!("模糊点: {} 条", ambiguities);
    println!("编码问题: {} 个", issues);
    println!("输出: {:?}", output_dir.join("extracted.yaml"));

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;

    #[test]
    fn test_default_sources_returns_four() {
        let sources = default_sources();
        assert_eq!(sources.len(), 4);
        assert!(sources.iter().any(|(n, _)| n == "bylaw"));
        assert!(sources.iter().any(|(n, _)| n == "handbook"));
        assert!(sources.iter().any(|(n, _)| n == "tutorial"));
        assert!(sources.iter().any(|(n, _)| n == "profile"));
    }

    #[test]
    fn test_read_text_returns_content() {
        let dir = std::env::temp_dir();
        let path = dir.join("_test_acquire_read.txt");
        let mut f = std::fs::File::create(&path).unwrap();
        writeln!(f, "hello world").unwrap();
        assert_eq!(read_text(&path), "hello world\n");
        let _ = std::fs::remove_file(&path);
    }

    #[test]
    fn test_read_text_missing_file() {
        let path = PathBuf::from("/nonexistent/file.md");
        assert_eq!(read_text(&path), "");
    }

    #[test]
    fn test_run_custom_input_file_reading() {
        let dir = std::env::temp_dir();
        let input = dir.join("_test_acquire_input.txt");
        std::fs::write(&input, "simple test content").unwrap();

        let args = AcquireArgs {
            input: input.to_string_lossy().to_string(),
            output: dir.join("_test_acquire_out").to_string_lossy().to_string(),
        };

        // 移除 API key 环境变量，确保无 key 时快速报错（不触发真实 LLM 调用）
        unsafe {
            std::env::remove_var("QTCLOUD_KNOWL_LLM_API_KEY");
            std::env::remove_var("DEEPSEEK_API_KEY");
        }
        let settings = Settings::load();
        let result = run(&args, &settings);
        assert!(result.is_err(), "无 API key 时应报错");

        let _ = std::fs::remove_file(&input);
        let _ = std::fs::remove_dir_all(&args.output);
    }
}
