import logging
from typing import Generator

from sqlalchemy import create_engine, Boolean, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String

from app.settings import get_settings

logger = logging.getLogger(__name__)

engine = None
SessionLocal = None


def get_engine():
    global engine
    if not engine:
        engine = create_engine(
            get_settings().db_file,
            # required for sqlite
            connect_args={"check_same_thread": False},
        )
    return engine


def get_session_maker():
    global SessionLocal
    if not SessionLocal:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return SessionLocal


def get_db() -> Generator:
    db = get_session_maker()()
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
    username = Column(String, nullable=True)
    start_time = Column(String, nullable=False)
    image = Column(String, nullable=False)
    command = Column(String, nullable=False)
    gpus = Column(Integer, nullable=False)
    dry_run = Column(Boolean, nullable=False)
    env = Column(String, nullable=False)


def init_db_schema():
    logger.info("Initializing database schema")
    Base.metadata.create_all(get_engine())
