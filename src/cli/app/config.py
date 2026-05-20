"""配置管理。

支持 Vault 读取 API key，通过 pydantic-settings 提供运行时路径。
"""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource
from quanttide import LocalStorage

try:
    from pydantic_vault import VaultSettingsSource
except ImportError:
    VaultSettingsSource = None


class Settings(BaseSettings):
    model_config = {"env_prefix": "QTCLOUD_KNOWL_"}

    data_home: Path = LocalStorage("qtcloud-knowl", vendor="quanttide").data_dir
    state_home: Path = LocalStorage("qtcloud-knowl", vendor="quanttide").state_dir
    sample_home: Optional[Path] = None

    llm_api_key: str = Field(
        default="",
        json_schema_extra=(
            {"vault_secret_path": "quanttide/deepseek", "vault_secret_key": "api_key"}
            if VaultSettingsSource
            else {}
        ),
    )

    @classmethod
    def settings_customise_sources(
        cls,
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
