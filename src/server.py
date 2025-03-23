import asyncio
import asyncpg

from app.manager import ServerManager


async def create_pool():
    return await asyncpg.create_pool(
        user='user',
        password='password',
        database='vm_db',
        host='db',
        port=5432,
        min_size=5,
        max_size=10
    )


async def main():
    pool = await create_pool()
    protocol = ServerManager(pool)

    server = await asyncio.start_server(
        protocol.handle_client, '0.0.0.0', 8888
    )

    addr = server.sockets[0].getsockname()
    print(f"Сервер работает на {addr}")

    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())