import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy_utils import database_exists, create_database
from dotenv import load_dotenv
from contextlib import contextmanager

Base = declarative_base()


def get_engine(user, passwd, host, port, db):
    url = f"postgresql://{user}:{passwd}@{host}:{port}/{db}"
    if not database_exists(url):
        create_database(url)

    engine = create_engine(url, echo=False)
    return engine

def get_engine_from_env():
    load_dotenv()

    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    return get_engine(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)

def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)

#call as with get_session(engine) as session
#runs what's inside the with block and saves the changes if anything goes rong it rolls back to the previous commit
@contextmanager
def get_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
