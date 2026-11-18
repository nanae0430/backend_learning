from models import Document, User
from sqlalchemy.orm import Session
from sqlalchemy import select
import pytest


def test_get_document(client, test_user, db_connection):
    with Session(bind=db_connection, join_transaction_mode="create_savepoint") as db:
        document = Document(user_id=test_user, title="GET Test Document")
        db.add(document)
        db.commit()
        db.refresh(document)
        doc_id = document.id

    response = client.get(f"/documents/{doc_id}")

    data = response.json()
    assert response.status_code == 200
    assert data["id"] == doc_id
    assert data["user_id"] == test_user
    assert data["title"] == "GET Test Document"


def test_get_document_not_found(client):
    miss_id = 2**63 - 1
    response = client.get(f"/documents/{miss_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"


def test_update_document(client, test_user, db_connection):
    with Session(bind=db_connection, join_transaction_mode="create_savepoint") as db:
        document = Document(user_id=test_user, title="Original Title")
        db.add(document)
        db.commit()
        db.refresh(document)
        doc_id = document.id

    response = client.patch(f"/documents/{doc_id}", json={"title": "updated title"})

    assert response.status_code == 200
    assert response.json()["title"] == "updated title"

    with Session(bind=db_connection, join_transaction_mode="create_savepoint") as db:
        document = db.get(Document, doc_id)

        assert document is not None
        assert document.title == "updated title"


def test_update_document_not_found(client):
    miss_id = 2**63 - 1
    response = client.patch(f"/documents/{miss_id}", json={"title": "updated title"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"


def test_delete_document(client, test_user, db_connection):
    with Session(bind=db_connection, join_transaction_mode="create_savepoint") as db:
        document = Document(user_id=test_user, title="Delete Test Document")
        db.add(document)
        db.commit()
        db.refresh(document)
        doc_id = document.id

    response = client.delete(f"/documents/{doc_id}")

    assert response.status_code == 204
    assert response.content == b""

    with Session(bind=db_connection, join_transaction_mode="create_savepoint") as db:
        document = db.get(Document, doc_id)

        assert document is None


def test_delete_document_not_found(client):
    miss_id = 2**63 - 1
    response = client.delete(f"/documents/{miss_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"


def test_transaction_isolation(db_connection):
    with Session(bind=db_connection, join_transaction_mode="create_savepoint") as db:

        # 1. 查询 username 为 pytest_user 的用户
        stmt = select(User).where(User.username == "pytest_user")
        # 2. 断言用户不存在
        result = db.execute(stmt)
        user = result.scalar_one_or_none()
        assert user is None


def test_create_document_missing_title(client):
    response = client.post("/documents", json={"user_id": 111})

    assert response.status_code == 422

    errors = response.json()["detail"]

    assert any(
        error["type"] == "missing" and error["loc"] == ["body", "title"]
        for error in errors
    )


@pytest.mark.parametrize(
    "title, error_type",
    [("", "string_too_short"), ("*" * 201, "string_too_long")],
    ids=["too short", "too long"],
)
def test_create_document_invalid_title(client, title, error_type):
    response = client.post("/documents", json={"user_id": 111, "title": title})

    assert response.status_code == 422

    errors = response.json()["detail"]

    assert any(
        error["type"] == error_type and error["loc"] == ["body", "title"]
        for error in errors
    )


@pytest.mark.parametrize(
    "title",
    ["Pytest Document", "*", "*" * 200],
    ids=["normal", "min-length", "max-length"],
)
def test_create_document_valid_title(client, test_user, db_connection, title):

    response = client.post("/documents", json={"user_id": test_user, "title": title})
    data = response.json()
    assert response.status_code == 201
    assert data["title"] == title
    assert isinstance(data["id"], int)

    doc_id = data["id"]
    with Session(bind=db_connection, join_transaction_mode="create_savepoint") as db:
        document = db.get(Document, doc_id)

        assert document is not None
        assert document.id == doc_id
        assert document.user_id == test_user
        assert document.title == title


def test_create_document_invalid_user(client, test_user):
    invalid_user = 2**63 - 1
    response = client.post(
        "/documents", json={"user_id": invalid_user, "title": "Foreign Key Test"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Database constraint violation"
    response = client.post(
        "/documents", json={"user_id": test_user, "title": "Foreign Key Test"}
    )
