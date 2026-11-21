import asyncio
import httpx
import time


async def fetch(client, name):
    # 1. 请求 http://127.0.0.1:8000/delay
    response = await client.get("http://127.0.0.1:8000/delay")
    # 2. 打印 name 和 HTTP 状态码
    print(f"name:{name}\tstatus_code:{response.status_code}")
    # 3. 返回响应结果
    return response.json()


async def main():
    start = time.perf_counter()

    async with httpx.AsyncClient() as client:
        asyncio.gather(fetch(client, "A"), fetch(client, "B"))

    elapsed = time.perf_counter() - start
    print(f"Elapsed: {elapsed:.2f}s")


asyncio.run(main())
