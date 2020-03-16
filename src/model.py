from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    level = Column(Integer)

    def title(self):
        if self.name:
            return self.name
        else:
            return '%d' % self.id

class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)

class Teach(Base):
    __tablename__ = 'teach'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer, ForeignKey('users.id'))
    question = Column(String(50))
    answer = Column(String(50))