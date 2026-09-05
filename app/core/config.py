from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    BREVO_API_KEY: str
    EMAIL_FROM: str
    FRONTEND_URL: str

    class Config:
        env_file = ".env"


settings = Settings()