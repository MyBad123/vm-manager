import asyncio
import json

from .credentials import Сredentials
from .disks import VirtualMachineDisk
from .virtual_machine import VirtualMachine


class ServerManager:
    def __init__(self, pool):
        self._v_credentials = Сredentials(pool)
        self._v_disks = VirtualMachineDisk(pool)
        self._v_machines = VirtualMachine(pool)

        # struct of connections and block for async requests
        self.connections = dict()
        self.lock = asyncio.Lock()

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"New connection from {addr}")

        try:
            while True:
                data = await reader.read(100)

                message = data.decode()
                print(f"Received {message} from {addr}")

                if message.startswith("EXIT"):
                    break

                # block create/update VM
                elif message.startswith('CREATE_VM'):
                    response = await self._v_machines.create(**json.loads(message[10:]))

                # block with getting list of VM
                elif message.startswith('USED_NOW_VM'):
                    ids = await self.get_connections()
                    response = await self._v_machines.used_now_list(ids)
                
                elif message.startswith('USED_VM'):
                    response = await self._v_machines.used_list()
                elif message.startswith('ALL_VM'):
                    response = await self._v_machines.list_vm()
                
                # block with login/logout
                elif message.startswith('LOGIN'):
                    response = await self._v_credentials.login(**json.loads(message[6:]))
                    
                    if response:
                        response = f"Вы подключились к {response[0][0]}"
                    else:
                        response = f"Ошибка подключения к {response[0][0]}"

                elif message.startswith('LOG_OUT'):
                    response = "Вы отключились от сервера"

                # block with list of disks
                elif message.startswith("ALL_DISKS"):
                    response = await self._v_disks.disk_list()

                else:
                    response = f"Hello, client at {addr}! You said: {message}"

                # response for client
                writer.write(response.encode())
                await writer.drain()

        except asyncio.CancelledError:
            print(f"Connection with {addr} was cancelled.")
        finally:
            print(f"Closing connection with {addr}")
            writer.close()
            await writer.wait_closed()

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
