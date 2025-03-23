import json

from .utils import Hash


class VirtualMachineSQL:
    """get data from db"""

    def __init__(self, pool):
        self.pool = pool
    
    def _fetch_vm_data(self, filters=None, ids_list=None):
        """Generic method to fetch VM data with optional filters and ID list"""
        
        query = f"""
            SELECT 
                vm.id AS vm_id,
                vm.ram_size,
                vm.cpu_count,
                ARRAY_AGG(vmd.disk_size) AS disk_sizes
            FROM 
                virtual_machines vm
            LEFT JOIN
                virtual_machines_disks vmd ON vm.id = vmd.vm_id
        """
        
        # Adding joins if filters are provided
        if filters:
            query += filters
        
        # If ids_list is provided, filter by those IDs
        if ids_list is not None:
            placeholders = ', '.join(['$' + str(i + 1) for i in range(len(ids_list))])
            query += f" AND vm.id IN ({placeholders})"
        
        query += """
            GROUP BY 
                vm.id;
        """
        
        return query

    async def _used_now_list(self, ids_list):
        """Fetch the list of currently used VMs"""
        
        filters = """
            INNER JOIN virtual_machine_credentials vmc ON vm.id = vmc.vm_id
            WHERE vmc.last_login IS NOT NULL
        """
        
        query = self._fetch_vm_data(filters=filters, ids_list=ids_list)
        
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *ids_list)
    
    async def _used_list(self):
        """Fetch the list of used VMs"""
        
        filters = """
            INNER JOIN virtual_machine_credentials vmc ON vm.id = vmc.vm_id
            WHERE vmc.last_login IS NOT NULL
        """
        
        query = self._fetch_vm_data(filters=filters)
        
        async with self.pool.acquire() as conn:
            return await conn.fetch(query)
    
    async def _list_vm(self):
        """Fetch the list of all VMs"""
        
        query = self._fetch_vm_data(filters=None)
        
        async with self.pool.acquire() as conn:
            return await conn.fetch(query)

    async def _create(self, **kwargs):
        """create vm with disk and credentials"""

        async with self.pool.acquire() as conn:
            async with conn.transaction():

                # create new VM
                create_vm_query = """
                    INSERT INTO virtual_machines (ram_size, cpu_count)
                    VALUES ($1, $2)
                    RETURNING id
                """

                vm_obj = await conn.fetch(create_vm_query, kwargs['ram_size'], kwargs['cpu_count'])

                # create login and password for new VM
                create_credentials_query = """
                    INSERT INTO virtual_machine_credentials (vm_id, login, password_hash)
                    VALUES ($1, $2, $3)
                """

                await conn.execute(create_credentials_query, vm_obj[0]['id'], 
                                   kwargs['login'], kwargs['password'])
                
                # create list of disks for VM
                create_disks_query = """
                    INSERT INTO virtual_machines_disks (vm_id, disk_size)
                    VALUES ($1, $2)
                """

                await conn.executemany(
                    create_disks_query, [[vm_obj[0]['id'], disk] for disk in kwargs['disks']]
                )

    async def _update(self, **kwargs):
        """method for update VM"""

        query = """
            SELECT 
                vm.id,
                vm.ram_size,
                vm.cpu_count,
                ARRAY(
                    SELECT vmd.id
                    FROM virtual_machines_disks vmd
                    WHERE vmd.vm_id = vm.id
                    ORDER BY vmd.created_at
                ) AS disk_sizes,
                vcreds.login AS credentials_login,
                vcreds.password_hash AS credentials_password_hash,
                vcreds.last_login AS credentials_last_login
            FROM 
                virtual_machines vm
            LEFT JOIN 
                virtual_machine_credentials vcreds ON vcreds.vm_id = vm.id
            WHERE 
                vm.id = $1;
        """

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                vm_obj = await conn.fetchrow(query, kwargs['id'])
                if not vm_obj:
                    raise ValueError('Такого объекта нет в базе')

                # update virtual_machines obj
                if kwargs.get('ram_size') or kwargs.get('cpu_count'):
                    ram_size = kwargs.get('ram_size', vm_obj[1])
                    cpu_count = kwargs.get('cpu_count', vm_obj[2])

                    query = """
                        UPDATE virtual_machines
                        SET ram_size = $1, cpu_count = $2
                        WHERE id = $3;
                    """
                    
                    await conn.execute(query, ram_size, cpu_count, kwargs['id'])
                    
                # update credentials
                if kwargs.get('login') or kwargs.get('password'):
                    login = kwargs.get('login', vm_obj[4])
                    password = kwargs.get('password', vm_obj[5])

                    query = """
                        UPDATE virtual_machine_credentials
                        SET login = $1, password_hash = $2
                        WHERE vm_id = $4;
                    """

                    await conn.execute(query, login, password, kwargs['id'])

                # update disk size
                create_struct = list()

                for key, disk in enumerate(kwargs.get('disks', [])):
                    if key >= len(vm_obj[3]):
                        create_struct.append([vm_obj[0], disk])
                        continue

                    query = """
                        UPDATE virtual_machines_disks
                        SET disk_size = $1
                        WHERE id = $2;
                    """

                    await conn.execute(query, disk, vm_obj[3][key])

                if create_struct:
                    create_disks_query = """
                        INSERT INTO virtual_machines_disks (vm_id, disk_size)
                        VALUES ($1, $2)
                    """

                    await conn.executemany(create_disks_query, create_struct) 


class VirtualMachine(VirtualMachineSQL):
    """Work with data from DB and format it for response to the client"""

    @staticmethod
    def struct_row(rows):
        """Converts the rows of VM data into a list of dictionaries"""
        
        result = []
        for row in rows:
            result.append({
                'vm_id': row['vm_id'],
                'ram_size': row['ram_size'],
                'cpu_count': row['cpu_count'],
                'disk_sizes': row['disk_sizes']
            })
    
        return result

    async def used_now_list(self, **kwargs):
        """Fetch and format the list of currently used VMs"""

        if not kwargs.get('ids_list'):
            return json.dumps([])
        
        rows = await super()._used_now_list(**kwargs)
        return json.dumps(VirtualMachine.struct_row(rows))
    
    async def used_list(self):
        """Fetch and format the list of used VMs"""
        
        rows = await super()._used_list()
        return json.dumps(VirtualMachine.struct_row(rows))
    
    async def list_vm(self):
        """Fetch and format the list of all VMs"""
        
        rows = await super()._list_vm()
        return json.dumps(VirtualMachine.struct_row(rows))
    
    async def create(self, **kwargs):
        """method for create VM"""

        # work with password
        if kwargs.get('password'):
            kwargs['password'] = Hash.hash_password_with_key(kwargs['password'])
        
        await super()._create(**kwargs)
        return "Вы успешно создали виртуальную машину"
    
    async def update(self, **kwargs):
        """method for update VM"""

        # control id
        if not kwargs.get('id'):
            return "Ошибка обновления виртуальной машины: нет ID для обновления"
        
        # work with password
        if kwargs.get('password'):
            kwargs['password'] = Hash.hash_password_with_key(kwargs['password'])

        try:
            await super()._update(**kwargs)
        except ValueError as e:
            return f"Ошибка обновления виртуальной машины: {e}"
        
        return "Вы успешно убновили виртуальную машину"
