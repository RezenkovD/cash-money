from authlib.integrations.base_client import OAuthError
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session
from starlette.config import Config
from starlette.requests import Request
from starlette.responses import RedirectResponse
from fastapi import Depends, APIRouter

from database import get_db
from services import create_user, get_user

router = APIRouter(
    tags=["registration"],
)

CONF_URL = "https://accounts.google.com/.well-known/openid-configuration"

config = Config("src/.env")
oauth = OAuth(config)

oauth.register(
    name="google",
    server_metadata_url=CONF_URL,
    client_kwargs={
        "scope": "openid email profile",
        "prompt": "select_account",
    },
)


@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth")
async def auth(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return error.error
    user = token["userinfo"]
    if user:
        request.session["user"] = dict(user)
        db_user = get_user(db, login=user["email"])
        if db_user:
            return RedirectResponse(url="/")
        create_user(
            db=db,
            login=user["email"],
            first_name=user["given_name"],
            last_name=user["family_name"],
            picture=user["picture"],
        )
    return RedirectResponse(url="/")


@router.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/")
