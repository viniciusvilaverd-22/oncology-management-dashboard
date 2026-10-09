from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Gestão Integrada da Oncologia"
    app_env: str = "dev"
    auth_db_path: str = "../data/auth.db"
    session_hours: int = 8
    app_secure_cookies: bool = False
    data_adapter: str = ""
    default_payer_id: int = 100

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
