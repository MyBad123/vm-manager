import asyncio
import json

from .credentials import Credentials
from .disks import VirtualMachineDisk
from .virtual_machine import VirtualMachine


class ServerManager:
    def __init__(self, pool):
        self.connections = dict()
        self.lock = asyncio.Lock()

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"New connection from {addr}")

        try:
            while True:
                size_data = await reader.read(4)
                data_size = int.from_bytes(size_data, byteorder='big')

                data = await reader.read(data_size)

                if not data:
                    print(f"Connection with {addr} lost.")
                    break

                message = data.decode()
                print(f"Received {message} from {addr}")

                if message.startswith("EXIT"):
                    break

                # work with commands
                response = await self.process_message(addr, message)

                # send response with bytes
                response = response.encode()

                writer.write((len(response).to_bytes(4, byteorder='big')))
                await writer.drain()

                writer.write(response)
                await writer.drain()

        except asyncio.CancelledError:
            print(f"Connection with {addr} was cancelled.")
        finally:
            print(f"Closing connection with {addr}")
            writer.close()
            await writer.wait_closed()

    async def process_message(self, addr, message):
        """work with commands"""

        # block create/update VM
        if message.startswith('CREATE_VM'):
            response = await self._v_machines.create(**json.loads(message[10:]))

        elif message.startswith('UPDATE_VM'):
            response = await self._v_machines.update(**json.loads(message[10:]))

        # block with getting list of VM
        elif message.startswith('USED_NOW_VM'):
            ids = await self.get_connections()
            response = await self._v_machines.used_now_list(ids_list=ids)
        
        elif message.startswith('USED_VM'):
            response = await self._v_machines.used_list()
        
        elif message.startswith('ALL_VM'):
            response = await self._v_machines.list_vm()
        
        # block with login/logout
        elif message.startswith('LOGIN'):
            response = await self._v_credentials.login(**json.loads(message[6:]))
            
            if response:
                await self.set_connection(addr, response)
                response = f"Вы подключились к виртуальной машине"
            else:
                response = f"Ошибка подключения к виртуальной машине"

        elif message.startswith('LOG_OUT'):
            await self.drop_connection(addr)
            response = "Вы отключились от сервера"

        # block with list of disks
        elif message.startswith("ALL_DISKS"):
            response = await self._v_disks.disk_list()

        else:
            response = f"Hello, client at {addr}! You said: {message}"

        return response

    async def set_connection(self, key, vm_id):
        """set new connection of VM to struct"""

        async with self.lock:
            self.connections.update({key: vm_id})

    async def drop_connection(self, key):
        """drop connection of VM to struct"""

        async with self.lock:
            self.connections.pop(key, None)

    async def get_connections(self):
        """get VM with activa connections"""

        async with self.lock:
            return [self.connections[key] for key in self.connections.keys()]
