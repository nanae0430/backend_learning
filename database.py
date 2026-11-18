import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()


class Base(DeclarativeBase):
    pass


url = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password=os.environ["MYSQL_PASSWORD"],
    host="127.0.0.1",
    port=3307,
    database="rag_learning",
)
test_url = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password=os.environ["MYSQL_PASSWORD"],
    host="127.0.0.1",
    port=3307,
    database="rag_learning_test",
)

engine = create_engine(url, pool_pre_ping=True)
test_engine = create_engine(test_url, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine)
TestSessionLocal = sessionmaker(bind=test_engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
