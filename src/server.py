import asyncio
import asyncpg

from app.manager import ServerManager


async def create_pool():
    return await asyncpg.create_pool(
        user='user',
        password='password',
        database='vm_db',
        host='127.0.0.1',
        port=5433,
        min_size=5,
        max_size=10
    )


async def main():
    pool = await create_pool()
    protocol = ServerManager(pool)

    server = await asyncio.start_server(
        protocol.handle_client, '127.0.0.1', 8888
    )

    addr = server.sockets[0].getsockname()
    print(f"Сервер работает на {addr}")

    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())