import logging
from datetime import datetime

from authlib.integrations.starlette_client import OAuth
from fastapi import Depends, HTTPException
from pydantic.schema import date
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


def transform_date_or_422(date_: str) -> date:
    """
    '2021-01' -> datetime.date(2021, 01, 01) else raise HTTP_422
    """
    try:
        transformed_date = datetime.strptime(date_, "%Y-%m").date().replace(day=1)
    except ValueError:
        logging.info(f"{date_} has incorrect date format")
        raise HTTPException(
            status_code=422,
            detail=f"{date_} has incorrect date format, but should be YYYY-MM",
        )
    return transformed_date
