import uvicorn
from fastapi import FastAPI
from fastapi_pagination import add_pagination
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from config import settings, ALLOWED_HOSTS
from routers import (
    category,
    expense,
    group,
    invitation,
    registration,
    replenishment,
    user,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"https://{origin}" for origin in ALLOWED_HOSTS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.include_router(registration.router)
app.include_router(group.router)
app.include_router(user.router)
app.include_router(invitation.router)
app.include_router(category.router)
app.include_router(expense.router)
app.include_router(replenishment.router)

add_pagination(app)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True,
    )
