import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class BookCategory(Base):
    __tablename__ = 'bookCategory'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class BookItem(Base):
    __tablename__ = 'bookItem'

    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    author = Column(String(250))
    bookCategory_id = Column(Integer, ForeignKey('bookCategory.id'))
    bookCategory = relationship(BookCategory)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {

            'id': self.id,
            'title': self.title,
            'author': self.author,
        }



engine = create_engine('sqlite:///database_setup.db')


Base.metadata.create_all(engine)
