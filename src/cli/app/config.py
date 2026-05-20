"""knowl 项目配置 — 从 Vault 读取 LLM API key。"""

from pydantic import Field
from pydantic_settings import PydanticBaseSettingsSource
from pydantic_vault import VaultSettingsSource

from quanttide_agent.config import Settings as _BaseSettings


class Settings(_BaseSettings):
    llm_api_key: str = Field(
        default="",
        json_schema_extra={
            "vault_secret_path": "quanttide/deepseek",
            "vault_secret_key": "api_key",
        },
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[_BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            VaultSettingsSource(settings_cls),
            file_secret_settings,
        )


settings = Settings()
