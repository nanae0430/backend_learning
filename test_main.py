def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_search(client):
    response = client.get("/search", params={"query": "Transformer"})
    assert response.status_code == 200
    assert response.json()["query"] == "Transformer"
    assert response.json()["top_k"] == 5


def test_get_document(client):
    response = client.get("/documents/abc")

    assert response.status_code == 422
