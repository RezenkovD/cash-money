import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from config import settings
from database import Base, get_db
from main import app as main_app

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


main_app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
@pytest.mark.usefixtures("create_test_database")
def connection():
    with engine.connect() as connection:
        SessionLocal.configure(bind=connection)
        yield connection


@pytest.fixture(scope="function", autouse=True)
def _transaction_wrap(connection):
    transaction = connection.begin()
    try:
        yield connection
    finally:
        transaction.rollback()


@pytest.fixture(scope="function")
def session():
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    if not "test" in settings.SQLALCHEMY_DATABASE_URI:
        raise ValueError("Please connect the test database!")
    try:
        if database_exists(settings.SQLALCHEMY_DATABASE_URI):
            drop_database(settings.SQLALCHEMY_DATABASE_URI)
        create_database(settings.SQLALCHEMY_DATABASE_URI)
        yield
    finally:
        drop_database(settings.SQLALCHEMY_DATABASE_URI)


client = TestClient(main_app)
