from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bot.utils import BTConfigParser

parser = BTConfigParser()
db_user = parser.db_user
db_password = parser.db_password
db_url = parser.db_url
db_port = parser.db_port
db_database = parser.db_database

engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}'.format(db_user, db_password, db_url, db_port, db_database))
DBSession = sessionmaker(bind=engine)


@contextmanager
def session_scope(Session):
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
