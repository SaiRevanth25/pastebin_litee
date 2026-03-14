from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    # API Settings

    API_BASE_URL: str = ""
    FRONTEND_URL: str = ""
    ENVIRONMENT: str = ""

    # Database Settings
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )

    # Env settings for logging customization
    ENV_MODE: str = "LOCAL"
    LOG_LEVEL: str = "INFO"

settings = Settings()
