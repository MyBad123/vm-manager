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
                vm.id,
                vmc.id
            FROM 
                virtual_machine_credentials vmc
            INNER JOIN 
                virtual_machines vm
            ON 
                vmc.vm_id = vm.id
            WHERE vmc.login = $1 AND vmc.password_hash = $2 AND vm.id = $3
        """

        update_query = """
            UPDATE virtual_machine_credentials
            SET last_login = CURRENT_TIMESTAMP
            WHERE vm_id = $1;
        """

        async with self.pool.acquire() as conn:
            db_data = await conn.fetchrow(query, kwargs['login'], kwargs['password'], kwargs['vm_id'])
            
            if db_data:
                await conn.execute(update_query, db_data[1])

            return db_data
        

class Сredentials(СredentialsSQL):
    """work with response"""

    async def login(self, **kwargs):
        authenticated_data = await super()._login(**kwargs)
        if authenticated_data:
            return authenticated_data[0]
