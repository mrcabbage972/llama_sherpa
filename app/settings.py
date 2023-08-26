import pathlib
from pydantic.v1 import BaseSettings

REPO_ROOT = pathlib.Path(__file__).parent.parent.resolve()

class Settings(BaseSettings):
    db_file = f"sqlite:///{REPO_ROOT}/example.db"


settings = Settings()