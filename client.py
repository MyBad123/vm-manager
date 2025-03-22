import asyncio
import json


async def send_message():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    print("Соединение с сервером установлено")

    while True:
        message = input("Введите сообщение: ")

        if message.upper() == 'LOGIN':
            login = input("Введите имя пользователя: ")
            password = input("Введите пароль: ")
            vm_id = input("Введите ID виртуальной машины: ")

            data = {
                'login': login,
                'password': password,
                'vm_id': vm_id
            }

            message = f"LOGIN {json.dumps(data)}"

        if message.upper() == 'CREATE_VM':
            ram_size = input("Введите количество памяти: ")
            cpu_count = input("Введите число ядер: ")

            if not ram_size.isdigit() or cpu_count.isdigit():
                print('введите целочисленные значения для ядер или памяти')
                continue

            # block with credentials
            login = input("Введите имя пользователя: ")
            password = input("Введите пароль: ")

            # block with disk
            disks = input("Введите размер дисков через пробел: ")
            try:
                disks = list(map(int, disks.split()))
            except ValueError:
                print("Ошибка! Пожалуйста, введите только целые числа через пробел.")
                continue

            data = {
                'ram_size': ram_size,
                'cpu_count': cpu_count,
                'login': login,
                'password': password,
                'disks': disks
            }

            message = f"CREATE_VM {json.dumps(data)}"

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
