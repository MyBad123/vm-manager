import asyncio

async def send_message(writer):
    while True:
        message = input("Введите сообщение для отправки: ")
        writer.write(message.encode())  # Отправляем сообщение
        await writer.drain()  # Ожидаем, что сообщение будет отправлено

async def main():
    server_host = 'localhost'  # Адрес сервера
    server_port = 8888         # Порт сервера

    # Устанавливаем асинхронное соединение с сервером
    reader, writer = await asyncio.open_connection(server_host, server_port)

    print(f'Подключено к серверу {server_host}:{server_port}')

    # Запускаем отправку сообщений
    await send_message(writer)

    # Закрываем соединение
    writer.close()
    await writer.wait_closed()

# Запуск основного события
asyncio.run(main())
