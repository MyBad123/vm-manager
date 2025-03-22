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
                    VALUES ($1, $2),
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
