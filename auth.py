from fastapi_login import LoginManager

SECRET = "super-secret-key"
manager = LoginManager(SECRET, '/login', use_cookie=True)

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
