"""配置管理。

支持 Vault 读取 API key，通过 pydantic-settings 提供运行时路径。
"""

from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

try:
    from pydantic_vault import VaultSettingsSource
except ImportError:
    VaultSettingsSource = None


class Settings(BaseSettings):
    model_config = {"env_prefix": "QTCLOUD_KNOWL_"}

    data_home: Optional[Path] = None
    state_home: Optional[Path] = None

    llm_api_key: str = Field(
        default="",
        json_schema_extra=(
            {"vault_secret_path": "quanttide/deepseek", "vault_secret_key": "api_key"}
            if VaultSettingsSource
            else {}
        ),
    )
    llm_model: str = Field(default="deepseek-chat")
    llm_base_url: str = Field(default="")
    sample_home: Optional[Path] = None

    @field_validator("data_home", "state_home", "sample_home", mode="before")
    @classmethod
    def _empty_str_to_none(_, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    @model_validator(mode="after")
    def _default_paths(self):
        if self.data_home is None:
            self.data_home = Path.cwd() / "data"
        if self.state_home is None:
            self.state_home = self.data_home / ".state"
        if self.sample_home is None:
            self.sample_home = self.data_home / "samples"
        return self

    @classmethod
    def settings_customise_sources(
        _,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        sources = (init_settings, env_settings, dotenv_settings)
        if VaultSettingsSource:
            sources += (VaultSettingsSource(settings_cls),)
        return sources + (file_secret_settings,)


settings = Settings()
