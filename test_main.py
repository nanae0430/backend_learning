import main


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_search(client, monkeypatch):
    def fake_cached_search(query, top_k):
        return {"query": query, "top_k": top_k, "results": []}

    monkeypatch.setattr(main, "cached_search", fake_cached_search)

    response = client.get("/search", params={"query": "Transformer"})
    assert response.status_code == 200
    assert response.json()["query"] == "Transformer"
    assert response.json()["top_k"] == 5


def test_get_document(client):
    response = client.get("/documents/abc")

    assert response.status_code == 422
