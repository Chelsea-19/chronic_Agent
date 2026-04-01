from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'CarePilot CN Platform+'
    app_env: str = 'dev'
    api_prefix: str = '/api/v1'
    frontend_origin: str = 'http://127.0.0.1:8000'
    auth_bearer_token: str = 'dev-token'
    database_url: str = 'sqlite:///./carepilot_cn.db'
    default_window_days: int = 14
    export_dir: str = './exports'
    enable_fake_llm: bool = True
    default_llm_model: str = 'gpt-4o-mini'

    @property
    def export_path(self) -> Path:
        p = Path(self.export_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()
