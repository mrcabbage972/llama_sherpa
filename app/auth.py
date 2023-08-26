from fastapi_login import LoginManager

from app.db.db import User, SessionLocal

# TODO: move to settings
SECRET = "super-secret-key"

class NotAuthenticatedException(Exception):
    pass

manager = LoginManager(SECRET, '/login', use_cookie=True, custom_exception=NotAuthenticatedException)

# TODO: remove, not used anymore
DB = {
    'users': {
        'johndoe': {
            'name': 'John Doe',
            'password': 'secret'
        }
    }
}

@manager.user_loader()
def query_user(user_id: str):
    """
    Get a user from the db
    :param user_id: E-Mail of the user
    :return: None or the user object
    """
    sess = SessionLocal()
    user = sess.query(User).where(User.username == user_id).one()

    return user.__dict__ if user else None
