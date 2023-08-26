from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException

SECRET = "super-secret-key"

class NotAuthenticatedException(Exception):
    pass

manager = LoginManager(SECRET, '/login', use_cookie=True, custom_exception=NotAuthenticatedException)

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
    return DB['users'].get(user_id)
