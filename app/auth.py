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


