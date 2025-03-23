import json
from datetime import datetime


class СredentialsSQL:
    """getting data from db"""

    def __init__(self, pool):
        self.pool = pool

    async def _login(self, **kwargs):
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
            WHERE vmc.login = $1 AND vmc.password_hash = $2 AND vm.id = $3
        """

        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, kwargs['login'], kwargs['password'], kwargs['vm_id'])
        

class Сredentials(СredentialsSQL):
    """work with response"""

    async def login(self, **kwargs)
        is_authenticated = await super()._login(**kwargs)
        if is_authenticated:
            return True
        
        return False
    