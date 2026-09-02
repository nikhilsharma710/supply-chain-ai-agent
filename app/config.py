from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    '''Application configuration, loaded from .env.'''

    openai_api_key: str

    model_name: str = 'gpt-4.1-mini'
    model_temperature: float = 0.0
    model_max_tokens: int = 2048

    database_host: str = 'localhost'
    database_port: int = 5432
    database_name: str = 'supply_chain'
    database_username: str
    database_password: str

    model_config = SettingsConfigDict(
        env_file='.env',
        extra='ignore',
        protected_namespaces=()
    )

settings = Settings()