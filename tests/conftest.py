from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db import _get_db
from src.main import app
from src.repo import Base

DATABASE_URL = 'sqlite:///:memory:'
PREDEFINED_UUIDS = [
    'ccf696f7-dcdd-4e4a-a79e-37360507211a',
    'af487174-b85c-4ffc-8127-5dc035fb8f2f',
    'abb64fc8-cc5f-40d2-9a04-6116a4820b2e',
    'd40267d6-132c-4d55-a070-f4a5f00645df',
]


@pytest.fixture(autouse=True)
def mock_uuid4():
    with patch('uuid.uuid4', side_effect=iter(PREDEFINED_UUIDS)):
        yield


# heavily borrowed the following from: https://stackoverflow.com/questions/67255653/how-to-set-up-and-tear-down-a-database-between-tests-in-fastapi
@pytest.fixture(scope='session')
def engine():
    engine = create_engine(DATABASE_URL)
    yield engine
    engine.dispose()


@pytest.fixture(scope='session')
def tables(engine):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(engine, tables):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session):
    app.dependency_overrides[_get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_db():
    mock = MagicMock()
    return mock


@pytest.fixture(autouse=True)
def override_db_dependency(mock_db):
    app.dependency_overrides[_get_db] = lambda: mock_db
