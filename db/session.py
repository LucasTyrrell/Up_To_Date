import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy_utils import database_exists, create_database
from dotenv import load_dotenv
from contextlib import contextmanager
from db.jobs import Base


def get_engine(user, passwd, host, port, db):
    url = f"postgresql://{user}:{passwd}@{host}:{port}/{db}"
    if not database_exists(url):
        create_database(url)

    engine = create_engine(url, echo=False)
    return engine

def get_engine_from_env():
    load_dotenv()

    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB_HOST = os.getenv("POSTGRES_HOST")
    DB_PORT = os.getenv("POSTGRES_PORT")
    DB_NAME = os.getenv("POSTGRES_NAME")

    return get_engine(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)

def init_db():
    engine = get_engine_from_env()
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

#run this file to restart the database
init_db()