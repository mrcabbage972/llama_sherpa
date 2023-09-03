from fastapi_login.exceptions import InvalidCredentialsException

from app.security import verify_password, hash_password
from app.db.db import User


class UserManager:
    def __init__(self, db):
        self.db = db

    def authenticate(self, username: str, password: str):
        user = self.get_user(username)

        if not user:
            raise InvalidCredentialsException
        elif not verify_password(password, user.password):
            raise InvalidCredentialsException

    def create_user(self, username: str, email: str, password: str):
        hashed_password = hash_password(password)

        user = User(username=username, email=email, password=hashed_password, is_superuser=False)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

    def get_user(self, username: str) -> User:
        return self.db.query(User).where(User.username == username).one()

    def get_users(self) -> list[User]:
        return self.db.query(User).all()

    def delete_user(self, username: str):
        user = self.db.query(User).where(User.username == username).one()
        self.db.delete(user)
        self.db.commit()

    def change_password(self, username: str, password: str):
        user = self.db.query(User).where(User.username == username).one()
        user.password = hash_password(password)
        self.db.commit()

    def make_superuser(self, username: str):
        user = self.db.query(User).where(User.username == username).one()
        user.is_superuser = True
        self.db.commit()
