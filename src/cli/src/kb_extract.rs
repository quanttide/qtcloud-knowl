//! 知识库抽取：从 .md 文档生成知识库 JSON（domain/ontologies/instances）。

use std::fs;
use std::path::Path;

use anyhow::{Context, Result};
use serde_json::Value;
use uuid::Uuid;

use crate::config::Settings;
use crate::llm::complete_json;

#[derive(clap::Args)]
pub struct KBExtractArgs {
    /// 源文档 .md 文件路径
    #[arg(long, short = 's')]
    pub source: String,
    /// 输出 JSON 目录路径
    #[arg(long, default_value = "data")]
    pub data_dir: String,
}

/// 条目通用允许字段（对齐 Python ALLOWED_FIELDS）。
const ALLOWED_FIELDS: [&str; 4] = ["id", "name", "label", "description"];
/// 实例条目额外允许 ontology（对齐 Python ALLOWED_INSTANCE_FIELDS）。
const ALLOWED_INSTANCE_FIELDS: [&str; 5] = ["id", "name", "label", "description", "ontology"];

/// 剥离 ``` 代码围栏（对齐 Python _strip_fences）。
/// 运行时由 complete_json 内部的 parse_structured_output 承担等价职责，
/// 此函数保留供单元测试对齐 Python 行为。
#[cfg_attr(not(test), allow(dead_code))]
fn strip_fences(text: &str) -> String {
    let text = text.trim();
    let text = if text.starts_with("```") {
        match text.split_once('\n') {
            // 去掉首行围栏（``` 或 ```json），保留其后内容
            Some((_, rest)) => rest,
            // 无换行的纯围栏（如 "```"），去掉前三个字符
            None => &text[3..],
        }
    } else {
        text
    };
    let text = if text.ends_with("```") {
        // 去掉末尾最后一次出现的 ``` 及其后内容
        &text[..text.rfind("```").unwrap_or(0)]
    } else {
        text
    };
    text.trim().to_string()
}

/// 只保留允许的字段，id 替换为 UUID v4（对齐 Python _clean）。
/// 非对象值按空对象处理（缺失字段默认空字符串）。
fn clean_item(item: &Value, is_instance: bool) -> Value {
    let fields: &[&str] = if is_instance {
        &ALLOWED_INSTANCE_FIELDS
    } else {
        &ALLOWED_FIELDS
    };
    let mut cleaned = serde_json::Map::new();
    for field in fields {
        let value = item
            .get(*field)
            .cloned()
            .unwrap_or(Value::String(String::new()));
        cleaned.insert((*field).to_string(), value);
    }
    // 原始 id 丢弃，统一用 UUID v4
    cleaned.insert("id".to_string(), Value::String(Uuid::new_v4().to_string()));
    Value::Object(cleaned)
}

/// 组装 {domain, ontologies, instances} 输出结构（对齐 Python extract 的清洗段）。
fn clean_result(data: &Value) -> Value {
    let mut result = serde_json::Map::new();

    let domain = clean_item(data.get("domain").unwrap_or(&Value::Null), false);
    result.insert("domain".to_string(), domain);

    let ontologies = data
        .get("ontologies")
        .and_then(Value::as_array)
        .map(|arr| arr.iter().map(|o| clean_item(o, false)).collect::<Vec<_>>())
        .unwrap_or_default();
    result.insert("ontologies".to_string(), Value::Array(ontologies));

    let instances = data
        .get("instances")
        .and_then(Value::as_array)
        .map(|arr| arr.iter().map(|i| clean_item(i, true)).collect::<Vec<_>>())
        .unwrap_or_default();
    result.insert("instances".to_string(), Value::Array(instances));

    Value::Object(result)
}

pub fn run(args: &KBExtractArgs, settings: &Settings) -> Result<()> {
    let source_path = Path::new(&args.source);

    if !source_path.exists() {
        anyhow::bail!("文件不存在: {}", args.source);
    }
    if source_path.extension().and_then(|e| e.to_str()) != Some("md") {
        anyhow::bail!("仅支持 .md 文件: {}", args.source);
    }

    let prompt_path = Path::new(env!("CARGO_MANIFEST_DIR")).join("assets/prompts/extract.txt");
    let prompt_template = fs::read_to_string(&prompt_path)
        .map_err(|_| anyhow::anyhow!("prompt 模板不存在: extract.txt"))?;

    let stem = source_path
        .file_stem()
        .and_then(|s| s.to_str())
        .unwrap_or_default();
    let prompt = prompt_template.replace("{directory_name}", stem);

    let document = fs::read_to_string(source_path)
        .with_context(|| format!("读取源文件失败: {}", args.source))?;
    let filled = prompt.replace("{document}", &document);

    // Python 侧 llm.complete(filled) 为单条 user 消息；
    // complete_json 内部经 parse_structured_output 解析，已剥离 ```json 等代码围栏。
    let data = complete_json(settings, "", &filled)?;

    let result = clean_result(&data);

    let out_dir = Path::new(&args.data_dir);
    fs::create_dir_all(out_dir).with_context(|| format!("创建输出目录失败: {}", args.data_dir))?;
    let out_path = out_dir.join(format!("{stem}.json"));
    // serde_json 输出 UTF-8 原样（ensure_ascii=False 等价），2 空格缩进
    fs::write(&out_path, serde_json::to_string_pretty(&result)?)
        .with_context(|| format!("写入输出文件失败: {}", out_path.display()))?;

    println!("抽取完成。保存至 {}.", out_path.display());
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    // === strip_fences（对齐 Python test_strip_fences_*） ===

    #[test]
    fn test_strip_fences_json() {
        assert_eq!(strip_fences("```json\n{\"a\": 1}\n```"), "{\"a\": 1}");
    }

    #[test]
    fn test_strip_fences_no_fences() {
        assert_eq!(strip_fences("plain text"), "plain text");
    }

    #[test]
    fn test_strip_fences_leading_only() {
        assert_eq!(strip_fences("```\ncontent"), "content");
    }

    #[test]
    fn test_strip_fences_trailing_only() {
        assert_eq!(strip_fences("content\n```"), "content");
    }

    // === 字段清洗（不调 LLM，对齐 Python _clean / extract 清洗段） ===

    #[test]
    fn test_clean_item_keeps_allowed_fields_only() {
        let item = json!({
            "id": "orig-id",
            "name": "orig-name",
            "label": "测试标签",
            "description": "描述",
            "ontology": "onto-1",
            "extra": "丢弃",
        });
        let cleaned = clean_item(&item, false);
        let obj = cleaned.as_object().unwrap();
        assert_eq!(obj.len(), 4);
        assert_eq!(obj["name"], "orig-name");
        assert_eq!(obj["label"], "测试标签");
        assert_eq!(obj["description"], "描述");
        assert!(!obj.contains_key("extra"));
        assert!(!obj.contains_key("ontology"));
        // 原始 id 被 UUID v4 替换
        assert_uuid_v4(&obj["id"]);
    }

    #[test]
    fn test_clean_item_instance_keeps_ontology() {
        let item = json!({
            "id": "i1", "name": "n", "label": "L", "description": "D", "ontology": "onto-1"
        });
        let cleaned = clean_item(&item, true);
        let obj = cleaned.as_object().unwrap();
        assert_eq!(obj.len(), 5);
        assert_eq!(obj["ontology"], "onto-1");
    }

    #[test]
    fn test_clean_item_missing_fields_default_to_empty() {
        let cleaned = clean_item(&json!({"id": "x"}), false);
        let obj = cleaned.as_object().unwrap();
        assert_eq!(obj["name"], "");
        assert_eq!(obj["label"], "");
        assert_eq!(obj["description"], "");
    }

    #[test]
    fn test_clean_result_structure() {
        let data = json!({
            "domain": {"id": "d", "name": "d", "label": "领域", "description": "desc"},
            "ontologies": [{"id": "o1", "name": "o1", "label": "本体", "description": ""}],
            "instances": [{"id": "i1", "name": "i1", "label": "实例", "description": "", "ontology": "o1"}],
            "extra": "丢弃",
        });
        let result = clean_result(&data);
        let obj = result.as_object().unwrap();
        assert_eq!(obj.len(), 3);

        let domain = obj["domain"].as_object().unwrap();
        assert_eq!(domain.len(), 4);
        assert_eq!(domain["label"], "领域");
        assert_uuid_v4(&domain["id"]);

        let ontologies = obj["ontologies"].as_array().unwrap();
        assert_eq!(ontologies.len(), 1);
        assert_eq!(ontologies[0]["label"], "本体");
        assert_uuid_v4(&ontologies[0]["id"]);

        let instances = obj["instances"].as_array().unwrap();
        assert_eq!(instances.len(), 1);
        assert_eq!(instances[0]["label"], "实例");
        assert_eq!(instances[0]["ontology"], "o1");
        assert_uuid_v4(&instances[0]["id"]);
    }

    #[test]
    fn test_clean_result_missing_sections() {
        let result = clean_result(&json!({}));
        let obj = result.as_object().unwrap();
        assert_eq!(obj["domain"]["name"], "");
        assert!(obj["ontologies"].as_array().unwrap().is_empty());
        assert!(obj["instances"].as_array().unwrap().is_empty());
    }

    fn assert_uuid_v4(value: &Value) {
        let id = value.as_str().unwrap();
        assert_eq!(id.len(), 36);
        assert_eq!(
            Uuid::parse_str(id).unwrap().get_version(),
            Some(uuid::Version::Random)
        );
    }
}
