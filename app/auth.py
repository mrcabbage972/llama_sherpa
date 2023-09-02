import bcrypt
from fastapi_login import LoginManager

from app.db.db import User, get_session_maker
from app.settings import get_settings


class NotAuthenticatedException(Exception):
    pass


manager = LoginManager(get_settings().secret, '/login', use_cookie=True, custom_exception=NotAuthenticatedException)


@manager.user_loader()
def query_user(user_id: str):
    """
    Get a user from the db
    :param user_id: E-Mail of the user
    :return: None or the user object
    """
    sess = get_session_maker()()
    user = sess.query(User).where(User.username == user_id).one()

    return user.__dict__ if user else None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def hash_password(password: str) -> str:
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')
