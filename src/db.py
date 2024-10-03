import os
from typing import Generator, Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


engine = create_engine(os.environ['DATABASE_URL'])
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    """
    Set up the database for the application to use.
    """
    # NOTE: import necessary for table creation
    import src.repo
    Base.metadata.create_all(bind=engine)


def _get_db() -> Generator:
    """
    Dependency that provides a new database session for each request.
    """
    DB = session()
    try:
        yield DB
    finally:
        DB.close()


# dependency that can be used in route handlers
db_dependency = Annotated[session, Depends(_get_db)]
