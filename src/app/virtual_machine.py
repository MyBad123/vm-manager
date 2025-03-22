import asyncpg
from datetime import datetime

class VirtualMachine:
    def __init__(self, pool):
        self.pool = pool

    async def list(self):
        result = await self.conn.fetch("SELECT * FROM virtual_machines")
        return result
    
    async def authenticated_list(self, ids):
        query = f"""
        SELECT * FROM virtual_machines
        WHERE id IN {ids}
        """

        result = await self.conn.fetch(query, *ids)
        return result
    
    async def used_list(self):
        query = f"""
        SELECT 
            vm.id AS vm_id,
            vm.ram_size,
            vm.cpu_count,
            vmc.id AS credential_id,
            vmc.login,
            vmc.password_hash,
            vmc.last_login
        FROM 
            virtual_machines vm
        INNER JOIN 
            virtual_machine_credentials vmc ON vm.id = vmc.vm_id;
        WHERE vmc.last_login IS NOT NULL
        """
    
        result = await self.conn.fetch(query)
        return result

    async def create_vm(self, **kwargs):
        """create vm with disk and credentials"""

        async with self.pool.acquire() as conn:
            async with conn.transaction():

                create_vm_query = """
                    INSERT INTO virtual_machines (ram_size, cpu_count)
                    VALUES ($1, $2),
                    RETURNING id
                """

                vm_obj = await conn.fetch(create_vm_query, kwargs['ram_size'], kwargs['cpu_count'])
