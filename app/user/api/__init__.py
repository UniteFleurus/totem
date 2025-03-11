from app.main import app
from .auth import router as auth_router
from .users import router as user_router

app.include_router(auth_router)
app.include_router(user_router)
