from pydantic import BaseSettings


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URI: str
    TEST_SQLALCHEMY_DATABASE_URI: str
    APP_HOST: str
    APP_PORT: int
    SECRET_KEY: str
    SERVER_METADATA_URL: str


settings = Settings()
