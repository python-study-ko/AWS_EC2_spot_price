from sqlalchemy.pool import NullPool
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from raven import Client

from config import DB_ECHO, DB, SENTRY_DSN

engine_options = {'echo': DB_ECHO, 'poolclass': NullPool}
engine = create_engine(DB, **engine_options)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
sess = scoped_session(Session)

sentry = Client(dsn=SENTRY_DSN)
