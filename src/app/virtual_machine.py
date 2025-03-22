class VirtualMachine:
    def __init__(self, pool):
        self.pool = pool
    
    async def used_now_list(self, ids_list):
        """list of used VM on this moment"""

        if not ids_list:
            return []

        placeholders = ', '.join(['$' + str(i + 1) for i in range(len(ids_list))])
        
        query = f"""
            SELECT 
                vm.id AS vm_id,
                vm.ram_size,
                vm.cpu_count,
                ARRAY_AGG(vmd.disk_size) AS disk_sizes
            FROM 
                virtual_machines vm
            INNER JOIN 
                virtual_machine_credentials vmc ON vm.id = vmc.vm_id
            LEFT JOIN
                virtual_machines_disks vmd ON vm.id = vmd.vm_id
            WHERE 
                vm.id IN ({placeholders})
            GROUP BY 
                vm.id;
        """

        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *ids_list)
    
    async def used_list(self):
        """list of used VM"""

        query = f"""
            SELECT 
                vm.id AS vm_id,
                vm.ram_size,
                vm.cpu_count,
                ARRAY_AGG(vmd.disk_size) AS disk_sizes
            FROM 
                virtual_machines vm
            INNER JOIN 
                virtual_machine_credentials vmc ON vm.id = vmc.vm_id
            LEFT JOIN
                virtual_machines_disks vmd ON vm.id = vmd.vm_id
            WHERE 
                vmc.last_login IS NOT NULL
            GROUP BY 
                vm.id;
        """

        async with self.pool.acquire() as conn:
            return await conn.fetch(query)
        
    async def list_vm(self):
        """list of all VM"""

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
            GROUP BY 
                vm.id;
        """

        async with self.pool.acquire() as conn:
            return await conn.fetch(query)

    async def create(self, **kwargs):
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

        return f"Вы удачно создали новую виртуальную машину"

    async def update(self, **kwargs):
        """method for update VM"""

        query = """
            SELECT 
                vm.id,
                vm.ram_size,
                vm.cpu_count,
                ARRAY(
                    SELECT ROW(vmd.id, vmd.disk_size)
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
                vm_obj = await conn.fetchone(query, kwargs['id'])

                # update virtual_machines obj
                if kwargs['ram_size'] or kwargs['cpu_count']:
                    ram_size = kwargs.get('ram_size', vm_obj[1])
                    cpu_count = kwargs.get('cpu_count', vm_obj[2])

                    query = """
                        UPDATE virtual_machines
                        SET ram_size = $1, cpu_count = $2
                        WHERE id = $3;
                    """
                    
                    await conn.execute(query, ram_size, cpu_count, kwargs['id'])
                    
                # update credentials
                if kwargs['login'] or kwargs['password']:
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

                if kwargs['disks']:
                    for key, _ in enumerate(vm_obj[3]):
                        pass
                        
                    
                
