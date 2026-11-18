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

    # 2. 如果缓存存在
    #    打印 "Cache Hit"
    #    返回缓存结果
    if value is None:
        print("Cache Miss")
    else:
        print("Cache Hit")
    # 3. 如果缓存不存在
    #    打印 "Cache Miss"

    result = f"Search result for {query}"

    # 4. 将 result 写入 Redis，30 秒过期
    r.set(f"search:{query}", result)
    # 5. 返回 result
    return result
