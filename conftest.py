import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base, get_db, override_get_db, TestSessionLocal, test_engine
import models
from models import User
from sqlalchemy.orm import Session


@pytest.fixture(scope="session")
def setup_test_db():

    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(db_connection):
    def override_get_db():
        with Session(
            bind=db_connection, join_transaction_mode="create_savepoint"
        ) as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def test_user(db_connection):
    with Session(bind=db_connection, join_transaction_mode="create_savepoint") as db:
        user = User(username="pytest_user")

        db.add(user)
        db.commit()
        db.refresh(user)

    return user.id


@pytest.fixture
def db_connection(setup_test_db):
    connection = test_engine.connect()
    transaction = connection.begin()
    try:
        yield connection
    finally:
        transaction.rollback()
        connection.close()
