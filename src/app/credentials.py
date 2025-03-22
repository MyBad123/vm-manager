import json
from datetime import datetime


class Сredentials:
    def __init__(self, pool):
        self.pool = pool

    async def login(self, **kwargs):
        """auth by login and password"""

        query = f"""
            SELECT 
                vm.id
            FROM 
                virtual_machine_credentials vmc
            INNER JOIN 
                virtual_machines vm
            ON 
                vmc.vm_id = vm.id
            WHERE vmc.login = $1 AND vmc.password_hash = $2
        """

        async with self.pool.acquire() as conn:
            return await conn.fetch(query, kwargs['login'], kwargs['password'])
