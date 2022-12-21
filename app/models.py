from datetime import datetime

import sqlalchemy
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Table, Text, DateTime
from sqlalchemy.orm import relationship

from app.schemas import Base
metadata = sqlalchemy.MetaData()


follow_relations = Table('follow_relations', Base.metadata,
                         Column('follows_id', ForeignKey('profiles_id')),
                         Column('followed_by_id', ForeignKey('profiles_id'))
                         )


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)

    def __repr__(self):
        return f"<User(id={self.id}, " \
               f"email=\"{self.email}\", " \
               f"hashed_password=\"{self.hashed_password}\", " \



class UserProfile(Base):

    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    follows = relationship("UserProfile", secondary=follow_relations)


class Dweet(Base):

    __tablename__ = "dweets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    body = Column(Text,)
    created_at = Column(DateTime, default=datetime.now())
