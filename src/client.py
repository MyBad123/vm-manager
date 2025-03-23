import asyncio
import json


async def send_message():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8010)
    print("Соединение с сервером установлено")

    while True:
        is_response = False
        message = input("Введите сообщение: ")

        if message.upper() == 'LOGIN':
            login = input("Введите имя пользователя: ")
            password = input("Введите пароль: ")
            vm_id = input("Введите ID виртуальной машины: ")

            data = {
                'login': login,
                'password': password,
                'vm_id': int(vm_id)
            }

            message = f"LOGIN {json.dumps(data)}"

        elif message.upper() == 'CREATE_VM':
            ram_size = input("Введите количество памяти: ")
            cpu_count = input("Введите число ядер: ")

            if not ram_size.isdigit() or not cpu_count.isdigit():
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
                'ram_size': int(ram_size),
                'cpu_count': int(cpu_count),
                'login': login,
                'password': password,
                'disks': disks
            }

            message = f"CREATE_VM {json.dumps(data)}"

        elif message.upper() == 'UPDATE_VM':
            data = {}

            id_vm = input(f"Введите id виртуальной машины: ")
            if not id_vm.isdigit():
                print('введите целочисленное id для виртуальной машины')
                continue
            data['id'] = int(id_vm)

            # Обновление памяти
            update_ram = input(f"Хотите обновить память? (yes/no): ")
            if update_ram.lower() == 'yes':
                ram_size = input("Введите количество памяти: ")
                if not ram_size.isdigit():
                    print('введите целочисленное значение для памяти')
                    continue
                data['ram_size'] = int(ram_size)

            # Обновление числа ядер
            update_cpu = input(f"Хотите обновить текущее количество ядер? (yes/no): ")
            if update_cpu.lower() == 'yes':
                cpu_count = input("Введите число ядер: ")
                if not cpu_count.isdigit():
                    print('введите целочисленное значение для ядер')
                    continue
                data['cpu_count'] = int(cpu_count)

            # Обновление логина и пароля
            update_credentials = input(f"Хотите обновить текущий логин? (yes/no): ")
            if update_credentials.lower() == 'yes':
                login = input("Введите имя пользователя: ")
                password = input("Введите пароль: ")
                data['login'] = login
                data['password'] = password

            # Обновление дисков
            update_disks = input(f"Хотите обновить размер дисков? (yes/no): ")
            if update_disks.lower() == 'yes':
                disks = input("Введите размер дисков через пробел: ")
                try:
                    data['disks'] = list(map(int, disks.split()))
                except ValueError:
                    print("Ошибка! Пожалуйста, введите только целые числа через пробел.")
                    continue

            message = f"UPDATE_VM {json.dumps(data)}"

        elif message.upper() in ('USED_NOW_VM', 'USED_VM', 'ALL_VM'):
            is_response = True

        # send data
        length = len(message.encode())
        writer.write(length.to_bytes(4, byteorder='big'))
        await writer.drain()

        writer.write(message.encode())
        await writer.drain()

        # get data
        size_data = await reader.read(4)
        data_size = int.from_bytes(size_data, byteorder='big')

        data = await reader.read(data_size)

        if is_response:
            for vm in json.loads(data.decode()):
                print(f"Виртуальная машина ID: {vm['vm_id']}")
                print(f"  Оперативная память: {vm['ram_size']} ГБ")
                print(f"  Количество процессоров: {vm['cpu_count']}")
                print(f"  Размеры дисков: {', '.join(map(str, vm['disk_sizes']))}\n")

            continue

        print(f"Ответ от сервера: {data.decode()}")

        if message.lower() == 'exit':
            break

    print("Закрытие соединения с сервером")
    writer.close()
    await writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(send_message())
