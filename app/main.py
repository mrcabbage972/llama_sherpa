import logging

import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from app.auth import manager
from app.auth import NotAuthenticatedException
from app.data import TaskRegistry
from app.db.db import get_session_maker
from app.db.db import init_db_schema
from app.db.db import User
from app.routers import admin
from app.routers import backend
from app.routers import frontend
from app.routers import users
from app.routers.frontend import templates
from app.security import hash_password
from app.settings import get_settings
from app.user_manager import UserManager

logging.basicConfig()
logger = logging.getLogger(__name__)

init_db_schema()

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")

manager.useRequest(app)


def ensure_first_user():
    sess = get_session_maker()()
    users = sess.query(User).all()

    if len(users) == 0:
        password_hash = hash_password(get_settings().first_superuser_password)
        user = User(username=get_settings().first_superuser_username, password=password_hash,
                    email=get_settings().first_superuser_email, is_superuser=True)
        sess.add(user)
        sess.commit()
        sess.refresh(user)
        logger.info(f"Created first user: {user.username}")


ensure_first_user()

app.state.task_registry = TaskRegistry()
app.state.user_manager = UserManager(get_session_maker()())

app.include_router(frontend.router)
app.include_router(users.router)
app.include_router(backend.router)
app.include_router(admin.router)


@app.exception_handler(NotAuthenticatedException)
async def http_exception_handler(request, exc):
    return templates.TemplateResponse("no_creds.html", context={"request": request})


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8001)
