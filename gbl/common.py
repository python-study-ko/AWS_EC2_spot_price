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

URL_DICT = {'LINUX_PREV': 'http://a0.awsstatic.com/pricing/1/ec2/previous-generation/linux-od.min.js',
            'WIN_PREV': 'http://a0.awsstatic.com/pricing/1/ec2/previous-generation/mswin-od.min.js',
            'LINUX_CURRENT': 'http://a0.awsstatic.com/pricing/1/ec2/linux-od.min.js',
            'WIN_CURRENT': 'http://a0.awsstatic.com/pricing/1/ec2/mswin-od.min.js'}
