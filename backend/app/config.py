from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    JWT_ACCESS_EXPIRES_MIN: int = 15
    JWT_REFRESH_EXPIRES_DAYS: int = 7
    CORS_ORIGINS: str = "http://localhost:5173"

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

settings = Settings()