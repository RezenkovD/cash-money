from authlib.integrations.starlette_client import OAuth
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from starlette.config import Config
from starlette.requests import Request

from config import settings
from database import get_db
from services import get_user

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


def get_current_user(request: Request, db: Session = Depends(get_db)):
    try:
        user_info = request.session["user"]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized",
        )
    user = get_user(db, user_info["email"])
    return user
