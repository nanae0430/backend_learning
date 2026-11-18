import redis

r = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True,
)

print(r.ping())


def cached_search(query: str):
    key = f"search:{query}"

    # 1. 从 Redis 读取 key

    value = r.get(key)

    if value is None:
        print("Cache Miss")
        result = f"Search result for {query}"
        r.set(key, result, ex=30)
        return result

    else:
        print("Cache Hit")
        return value


print(cached_search("Transformer"))
print(cached_search("Transformer"))
