//! LLM 封装：quanttide-agent + QTCLOUD_KNOWL_* 配置。

use anyhow::{Context, Result};
use quanttide_agent::llm::{CompleteOptions, LLM};
use quanttide_agent::message::Message;

use crate::config::Settings;

fn llm(settings: &Settings) -> Result<LLM> {
    if settings.llm_api_key.is_empty() {
        anyhow::bail!(
            "未设置 LLM API Key（需通过环境变量 QTCLOUD_KNOWL_LLM_API_KEY 或 DEEPSEEK_API_KEY 配置）"
        );
    }
    let base_url = if settings.llm_base_url.is_empty() {
        "https://api.deepseek.com"
    } else {
        &settings.llm_base_url
    };
    Ok(LLM::new(
        &settings.llm_model,
        base_url,
        &settings.llm_api_key,
    ))
}

/// 完整对话，返回文本。
pub fn complete(settings: &Settings, system_prompt: &str, user_text: &str) -> Result<String> {
    let llm = llm(settings)?;
    let messages = vec![
        Message::new("system", system_prompt),
        Message::new("user", user_text),
    ];
    let resp = llm.complete(&messages, CompleteOptions::default())?;
    Ok(resp.content)
}

/// 对话并要求 JSON 输出，解析为 Value。
pub fn complete_json(
    settings: &Settings,
    system_prompt: &str,
    user_text: &str,
) -> Result<serde_json::Value> {
    let llm = llm(settings)?;
    let messages = vec![
        Message::new("system", system_prompt),
        Message::new("user", user_text),
    ];
    let options = CompleteOptions {
        response_format: Some(serde_json::json!({"type": "json_object"})),
        ..Default::default()
    };
    let resp = llm.complete(&messages, options)?;
    quanttide_agent::llm::parse_structured_output(&resp.content)
        .map_err(anyhow::Error::msg)
        .with_context(|| {
            format!(
                "LLM 返回结果解析失败: {}",
                &resp.content[..resp.content.len().min(200)]
            )
        })
}
