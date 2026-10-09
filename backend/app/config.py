from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    oracle_user: str
    oracle_password: str
    oracle_dsn: str
    app_name: str = 'Gestão Integrada da Oncologia'
    app_env: str = 'dev'
    auth_db_path: str = '../data/auth.db'
    session_hours: int = 8
    app_secure_cookies: bool = False

    model_config = SettingsConfigDict(
        env_file='../.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

settings = Settings()
