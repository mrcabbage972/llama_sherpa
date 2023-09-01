import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from app.auth import manager, NotAuthenticatedException, hash_password
from app.data import TaskRegistry
from app.db.db import SessionLocal, User
from app.routers import frontend, backend, users, admin
from app.routers.frontend import templates
from app.settings import get_settings

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.state.task_registry = TaskRegistry()
manager.useRequest(app)

app.include_router(frontend.router)
app.include_router(users.router)
app.include_router(backend.router)
app.include_router(admin.router)


@app.exception_handler(NotAuthenticatedException)
async def http_exception_handler(request, exc):
    return templates.TemplateResponse("no_creds.html", context={"request": request})


def ensure_first_user():
    sess = SessionLocal()
    users = sess.query(User).all()

    if len(users) == 0:
        password_hash = hash_password(get_settings().first_superuser_password)
        user = User(username=get_settings().first_superuser_username, password=password_hash,
                    email=get_settings().first_superuser_email, is_superuser=True)
        sess.add(user)
        sess.commit()
        sess.refresh(user)


if __name__ == '__main__':
    ensure_first_user()

    uvicorn.run(app, host="127.0.0.1", port=8001)
