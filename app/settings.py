import pathlib
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()


class Settings(BaseSettings):
    db_file: str = f"sqlite:///{REPO_ROOT}/example.db"
    secret: str = "super-secret-key" # TODO: move to .env

    model_config = SettingsConfigDict(env_file=".env", extra='allow')


@lru_cache()
def get_settings():
    return Settings()
