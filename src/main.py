import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from routers.registration import router as registration_router
from routers.group import router as group_router
from routers.user import router as user_router
from config import settings

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.include_router(registration_router)
app.include_router(group_router)
app.include_router(user_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True,
    )
