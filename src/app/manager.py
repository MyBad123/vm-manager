import asyncio

from .disks import VirtualMachineDisk
from .virtual_machine import VirtualMachine


class ServerManager:
    def __init__(self, pool):
        self._v_machines = VirtualMachine(pool)
        self._v_disks = VirtualMachineDisk(pool)

        # make block some resources
        self.lock = asyncio.Lock()

        # struct of connections
        self.connections = dict()

        # make struct for getting methods
        self.methods = {
            'auth': 'lol',
            'create_vm': 'create',
            'auth_vm': 'auth_vm',
            'used_vm': 'auth_vm',
            'ALL_VM': 'all_vm',
            'USED_VM': 'auth_vm',
            'update_vm': 'update_vm',
            'ALL_DISKS': self._v_disks.list
        }

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

                # block with command for work with VM
                elif message.startswith("ALL_DISKS"):
                    response = await self._v_disks.list()
                elif message.startswith('USED_VM'):
                    response = await self._v_machines.used_list()
                elif message.startswith('ALL_VM'):
                    response = await self._v_machines.list()
                else:
                    response = f"Hello, client at {addr}! You said: {message}"

                # Ответ клиенту
                writer.write(response.encode())
                await writer.drain()

        except asyncio.CancelledError:
            print(f"Connection with {addr} was cancelled.")
        finally:
            print(f"Closing connection with {addr}")
            writer.close()
            await writer.wait_closed()
