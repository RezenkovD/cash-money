import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from config import settings
from routers import category, expense, group, invitation, registration, user

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

app.include_router(registration.router)
app.include_router(group.router)
app.include_router(user.router)
app.include_router(invitation.router)
app.include_router(category.router)
app.include_router(expense.router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True,
    )
