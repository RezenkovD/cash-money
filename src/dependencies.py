from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

from config import settings


config = Config("src/.env")
oauth = OAuth(config)

oauth.register(
    name="google",
    server_metadata_url=settings.SERVER_METADATA_URL,
    client_kwargs={
        "scope": "openid email profile",
        "prompt": "select_account",
    },
)
