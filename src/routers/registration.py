from authlib.integrations.base_client import OAuthError
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse

from database import get_db
from dependencies import oauth
from models import User
from services import get_user

router = APIRouter(
    tags=["registration"],
)


@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth")
async def auth(*, db: Session = Depends(get_db), request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return error.error
    user = token["userinfo"]
    request.session["user"] = dict(user)
    db_user = get_user(db, login=user["email"])
    if not db_user:
        db_user = User(
            login=user["email"],
            first_name=user["given_name"],
            last_name=user["family_name"],
            picture=user["picture"],
        )
        db.add(db_user)
        db.flush()
        try:
            db.commit()
        except:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"An error occurred while create category",
            )
    return RedirectResponse(url="/")


@router.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/")
