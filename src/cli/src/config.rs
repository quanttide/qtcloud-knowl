//! 配置管理：QTCLOUD_KNOWL_* 环境变量（对齐 Python 版 settings 语义）。

use std::path::PathBuf;

pub struct Settings {
    /// 数据根目录（默认 ./data）
    pub data_home: PathBuf,
    /// 状态目录（默认 data_home/.state）
    pub state_home: PathBuf,
    /// LLM API Key（QTCLOUD_KNOWL_LLM_API_KEY，兼容 DEEPSEEK_API_KEY）
    pub llm_api_key: String,
    /// LLM 模型（默认 deepseek-chat）
    pub llm_model: String,
    /// LLM Base URL（默认 DeepSeek 官方）
    pub llm_base_url: String,
}

impl Settings {
    pub fn load() -> Self {
        let data_home =
            env_path("QTCLOUD_KNOWL_DATA_HOME").unwrap_or_else(|| PathBuf::from("data"));
        let state_home =
            env_path("QTCLOUD_KNOWL_STATE_HOME").unwrap_or_else(|| data_home.join(".state"));
        let llm_api_key = std::env::var("QTCLOUD_KNOWL_LLM_API_KEY")
            .or_else(|_| std::env::var("DEEPSEEK_API_KEY"))
            .unwrap_or_default();
        let llm_model =
            std::env::var("QTCLOUD_KNOWL_LLM_MODEL").unwrap_or_else(|_| "deepseek-chat".into());
        let llm_base_url = std::env::var("QTCLOUD_KNOWL_LLM_BASE_URL").unwrap_or_default();
        Self {
            data_home,
            state_home,
            llm_api_key,
            llm_model,
            llm_base_url,
        }
    }
}

fn env_path(key: &str) -> Option<PathBuf> {
    std::env::var(key)
        .ok()
        .filter(|v| !v.trim().is_empty())
        .map(PathBuf::from)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_load_defaults() {
        let s = Settings::load();
        assert_eq!(s.llm_model, "deepseek-chat");
        assert_eq!(s.data_home, PathBuf::from("data"));
    }
}
