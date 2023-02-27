from pydantic import BaseSettings


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URI: str
    APP_HOST: str
    APP_PORT: int


settings = Settings()
