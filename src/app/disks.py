import json


class VirtualMachineDiskSQL:
    """class for getting disks from db"""

    def __init__(self, pool):
        self.pool = pool

    async def _disk_list(self):
        """list of disks """
        
        query = """
            SELECT 
                vmd.id AS disk_id,
                vmd.vm_id,
                vmd.disk_size,
                vm.ram_size,
                vm.cpu_count
            FROM 
                virtual_machines_disks vmd
            INNER JOIN 
                virtual_machines vm
            ON 
                vmd.vm_id = vm.id;
        """

        async with self.pool.acquire() as conn:
            return await conn.fetch(query)


class VirtualMachineDisk(VirtualMachineDiskSQL):
    """convert SQL to string for response"""

    async def disk_list(self):
        result = await super()._disk_list()
        return json.dumps([dict(record) for record in result])

