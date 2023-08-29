from typing import Generator

from sqlalchemy import create_engine, Boolean, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String

from app.settings import settings

engine = create_engine(
    settings.db_file,
    # required for sqlite
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    db = SessionLocal()
    db.current_user_id = None
    try:
        yield db
    finally:
        db.close()

import typing as t

from sqlalchemy.ext.declarative import as_declarative, declared_attr


class_registry: t.Dict = {}


@as_declarative(class_registry=class_registry)
class Base:
    id: t.Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class User(Base):
    username = Column(String(256), primary_key=True)
    password = Column(String(256), nullable=False)
    email = Column(String, nullable=False)
    is_superuser = Column(Boolean, default=False)


class TaskSubmission(Base):
    id = Column(String, primary_key=True, index=True)
    start_time = Column(String, nullable=False)
    image = Column(String, nullable=False)
    command = Column(String, nullable=False)
    gpus = Column(Integer, nullable=False)
    dry_run = Column(Boolean, nullable=False)
    env = Column(String, nullable=False)

Base.metadata.create_all(engine)

pass