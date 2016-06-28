from sqlalchemy import types, Column
from sqlalchemy.ext.declarative import declarative_base


class BaseClass(object):
    __table_args__ = {}

    id = Column(types.Integer, primary_key=True, nullable=False, autoincrement=True)

    def __repr__(self):
        if self.id:
            return "<class {} ID: {}>".format(type(self).__name__, self.id)
        else:
            return "<class {} ID: None>".format(type(self).__name__)


Base = declarative_base(cls=BaseClass)
