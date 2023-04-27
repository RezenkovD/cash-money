import asyncio
import datetime

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

from tests.factories import (
    UserFactory,
    IconFactory,
    IconColorFactory,
    GroupFactory,
    UserGroupFactory,
    ColorFactory,
    CategoryFactory,
    CategoryGroupFactory,
    ExpenseFactory,
)


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


def async_return(result):
    as_res = asyncio.Future()
    as_res.set_result(result)
    return as_res


@pytest.fixture
def dependence_factory() -> dict:
    first_user = UserFactory()
    second_user = UserFactory()
    icon = IconFactory()
    color = ColorFactory()
    icon_color = IconColorFactory(icon_id=icon.id, color_id=color.id)
    first_group = GroupFactory(admin_id=first_user.id, icon_color_id=icon_color.id)
    UserGroupFactory(
        user_id=first_user.id,
        group_id=first_group.id,
    )
    factories = {
        "first_user": first_user,
        "second_user": second_user,
        "icon": icon,
        "color": color,
        "icon_color": icon_color,
        "first_group": first_group,
    }
    return factories


@pytest.fixture
@pytest.mark.usefixtures("dependence_factory")
def add_second_user_in_group(dependence_factory):
    factories = dependence_factory
    UserGroupFactory(
        user_id=factories["second_user"].id,
        group_id=factories["first_group"].id,
    )


@pytest.fixture
@pytest.mark.usefixtures("dependence_factory")
def activity(dependence_factory):
    filter_date = datetime.datetime(2022, 11, 12)
    factories = dependence_factory
    category = CategoryFactory()
    CategoryGroupFactory(category_id=category.id, group_id=factories["first_group"].id)
    first_expense = ExpenseFactory(
        user_id=factories["first_user"].id,
        group_id=factories["first_group"].id,
        category_id=category.id,
        time=filter_date,
    )
    activity = {
        "filter_date": filter_date,
        "category": category,
        "first_expense": first_expense,
    }
    return activity


@pytest.fixture
@pytest.mark.usefixtures("activity")
def update_activity(dependence_factory, activity):
    start_date = datetime.datetime(2022, 12, 10)
    end_date = datetime.datetime(2022, 12, 22)
    factories = dependence_factory
    second_group = GroupFactory(
        admin_id=factories["first_user"].id, icon_color_id=factories["icon_color"].id
    )
    UserGroupFactory(user_id=factories["first_user"].id, group_id=second_group.id)
    CategoryGroupFactory(category_id=activity["category"].id, group_id=second_group.id)
    second_expense = ExpenseFactory(
        user_id=factories["first_user"].id,
        group_id=second_group.id,
        category_id=activity["category"].id,
        time=start_date,
    )
    third_expense = ExpenseFactory(
        user_id=factories["first_user"].id,
        group_id=factories["first_group"].id,
        category_id=activity["category"].id,
        time=end_date,
    )
    update_activity = {
        "start_date": start_date,
        "end_date": end_date,
        "second_group": second_group,
        "second_expense": second_expense,
        "third_expense": third_expense,
    }
    return update_activity
