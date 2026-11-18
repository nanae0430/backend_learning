import redis, json

r = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True,
)

print(r.ping())


def cached_search(query: str):
    key = f"search:{query}"

    value = r.get(key)

    if value is not None:
        print("Cache Hit")
        return json.loads(value)

    print("Cache Miss")
    result = {
        "query": query,
        "top_k": 5,
        "results": [],
    }
    r.set(key, json.dumps(result), ex=30)
    return result


print(cached_search("Transformer"))
print(cached_search("Transformer"))
