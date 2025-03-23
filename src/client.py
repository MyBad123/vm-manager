import asyncio
import json


def get_user_input(message, is_int=False):
    """A function for receiving user input with an integer check."""
    
    while True:
        user_input = input(message)
        if is_int and user_input.isdigit():
            return int(user_input)
        elif not is_int:
            return user_input
        else:
            print("Ошибка! Пожалуйста, введите целое число.")


async def handle_create_vm():
    """Processing the creation of a VM."""

    ram_size = get_user_input("Введите количество памяти: ", True)
    cpu_count = get_user_input("Введите число ядер: ", True)
    
    login = get_user_input("Введите имя пользователя: ")
    password = get_user_input("Введите пароль: ")
    
    disks = input("Введите размер дисков через пробел: ")
    try:
        disks = list(map(int, disks.split()))
    except ValueError:
        print("Ошибка! Пожалуйста, введите только целые числа через пробел.")
        return None

    return {
        'ram_size': ram_size,
        'cpu_count': cpu_count,
        'login': login,
        'password': password,
        'disks': disks
    }


async def handle_update_vm():
    """Processing the VM update."""

    vm_id = get_user_input("Введите id виртуальной машины: ", True)
    data = {'id': vm_id}

    # Обновление параметров
    if get_user_input("Хотите обновить память? (yes/no): ").lower() == 'yes':
        data['ram_size'] = get_user_input("Введите количество памяти: ", True)

    if get_user_input("Хотите обновить количество ядер? (yes/no): ").lower() == 'yes':
        data['cpu_count'] = get_user_input("Введите число ядер: ", True)

    if get_user_input("Хотите обновить текущий логин? (yes/no): ").lower() == 'yes':
        data['login'] = get_user_input("Введите имя пользователя: ")
        data['password'] = get_user_input("Введите пароль: ")

    if get_user_input("Хотите обновить размер дисков? (yes/no): ").lower() == 'yes':
        disks = input("Введите размер дисков через пробел: ")
        try:
            data['disks'] = list(map(int, disks.split()))
        except ValueError:
            print("Ошибка! Пожалуйста, введите только целые числа через пробел.")
            return None

    return data


async def send_message():
    print("CREATE_VM - создать виртуальную машину")
    print("UPDATE_VM - обновить виртуальную машину")
    print("USED_NOW_VM - используемые виртуальные машины в текущий момент времени")
    print("USED_VM - использованные виртуальные машины когда-либо")
    print("ALL_VM - все виртуальные машины")
    print("LOGIN - подключиться к виртуальной машине")
    print("LOG_OUT - отключиться от виртуальной машины")
    print("ALL_DISKS - просмотр всех жестких дисков\n\n")

    reader, writer = await asyncio.open_connection('127.0.0.1', 8010)
    print("Соединение с сервером установлено")

    while True:
        is_response = False
        is_response_disk = False
        message = input("\n\nВведите сообщение: ").upper()

        if message == 'LOGIN':
            login = get_user_input("Введите имя пользователя: ")
            password = get_user_input("Введите пароль: ")
            vm_id = get_user_input("Введите ID виртуальной машины: ", True)

            data = {
                'login': login,
                'password': password,
                'vm_id': vm_id
            }
            message = f"LOGIN {json.dumps(data)}"

        elif message == 'CREATE_VM':
            data = await handle_create_vm()
            if data:
                message = f"CREATE_VM {json.dumps(data)}"
            else:
                continue

        elif message == 'UPDATE_VM':
            data = await handle_update_vm()
            if data:
                message = f"UPDATE_VM {json.dumps(data)}"
            else:
                continue

        elif message in ('USED_NOW_VM', 'USED_VM', 'ALL_VM'):
            is_response = True

        elif message == 'ALL_DISKS':
            is_response_disk = True

        # Sending data
        length = len(message.encode())
        writer.write(length.to_bytes(4, byteorder='big'))
        await writer.drain()

        writer.write(message.encode())
        await writer.drain()

        # Getting data
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

        if is_response_disk:
            for disk in json.loads(data.decode()):
                print(f"\nDisk ID: {disk['disk_id']}\n"
                      f"VM ID: {disk['vm_id']}\n"
                      f"Disk Size: {disk['disk_size']} GB\n"
                      f"RAM Size: {disk['ram_size']} GB\n"
                      f"CPU Count: {disk['cpu_count']}")
            
            continue

        print(f"Ответ от сервера: {data.decode()}")

        if message == 'EXIT':
            break

    print("Закрытие соединения с сервером")
    writer.close()
    await writer.wait_closed()


if __name__ == "__main__":
    asyncio.run(send_message())
