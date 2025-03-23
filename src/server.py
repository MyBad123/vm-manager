import asyncio
import asyncpg

from app.manager import ServerManager
from config import app_config


async def main():
    pool = await asyncpg.create_pool(**app_config.to_create_pool_dict())
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