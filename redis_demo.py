import redis, json

r = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True,
)


def cached_search(query: str, top_k: int = 5):
    key = f"search:{query}:{top_k}"

    value = r.get(key)

    if value is not None:
        print("Cache Hit")
        return json.loads(value)

    print("Cache Miss")
    result = {
        "query": query,
        "top_k": top_k,
        "results": [],
    }
    r.set(key, json.dumps(result), ex=30)
    return result


if __name__ == "__main__":
    print(r.ping())
    print(cached_search("Transformer", 5))
    print(cached_search("Transformer", 10))
    print(cached_search("Transformer", 5))
