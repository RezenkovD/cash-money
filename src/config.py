from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_HOST: str
    APP_PORT: int
    SECRET_KEY: str
    SERVER_METADATA_URL: str
    SQLALCHEMY_DATABASE_URI: str


settings = Settings()
