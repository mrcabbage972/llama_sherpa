import pathlib
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()


class Settings(BaseSettings):
    db_file: str = f"sqlite:///{REPO_ROOT}/internal.db"
    secret: str = "super-secret-key"  # TODO: move to .env

    first_superuser_username: str = "admin"
    first_superuser_password: str = None
    first_superuser_email: str = 'fake@email.com'

    # Flag that determines whether to require login for submitting jobs
    require_login_for_submit: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra='allow')


@lru_cache()
def get_settings():
    return Settings()
