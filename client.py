import asyncio
import json


async def send_message():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    print("Соединение с сервером установлено")

    while True:
        message = input("Введите сообщение: ")

        if message.upper() == 'LOGIN':
            username = input("Введите имя пользователя: ")
            password = input("Введите пароль: ")

            login_data = {
                'login': username,
                'password': password
            }

            message = f"LOGIN {json.dumps(login_data)}"


        writer.write(message.encode())
        await writer.drain()

        data = await reader.read(100)
        print(f"Ответ от сервера: {data.decode()}")

        if message.lower() == 'exit':
            break

    print("Закрытие соединения с сервером")
    writer.close()
    await writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(send_message())
