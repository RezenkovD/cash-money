from sqlalchemy import Column, Integer, String
from sqlalchemy_utils import URLType

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, nullable=False)
    first_name = Column(String, unique=False, nullable=False)
    last_name = Column(String, unique=False, nullable=False)
    picture = Column(URLType, nullable=True)
