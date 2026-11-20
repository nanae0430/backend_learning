import json
import redis_demo


def test_cache_miss(monkeypatch):
    def fake_get(key):
        return None

    monkeypatch.setattr(redis_demo.r, "get", fake_get)

    set_calls = []

    def fake_set(key, value, ex):
        set_calls.append((key, value, ex))

    monkeypatch.setattr(redis_demo.r, "set", fake_set)

    results = redis_demo.cached_search("Transformer", 5)

    assert results["query"] == "Transformer"
    assert results["top_k"] == 5

    assert set_calls[0][0] == "search:Transformer:5"
    assert set_calls[0][2] == 30


def test_cached_hit(monkeypatch):
    cached_data = {
        "query": "Transformer",
        "top_k": 5,
        "results": [],
    }

    def fake_get(key):
        return json.dumps(cached_data)

    monkeypatch.setattr(redis_demo.r, "get", fake_get)

    set_calls = []

    def fake_set(key, value, ex):
        set_calls.append((key, value, ex))

    monkeypatch.setattr(redis_demo.r, "set", fake_set)

    results = redis_demo.cached_search("Transformer", 5)

    assert results == cached_data

    assert set_calls == []
