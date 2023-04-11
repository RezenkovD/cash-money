import factory
from sqlalchemy.orm import scoped_session

from tests.conftest import SessionLocal


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = scoped_session(SessionLocal)
        sqlalchemy_session_persistence = "commit"
