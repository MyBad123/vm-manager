import json
from datetime import datetime

class VirtualMachineDisk:
    def __init__(self, conn):
        self.conn = conn

    async def list(self):
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

        result = await self.conn.fetch(query)
        return json.dumps(result)

    # Получение дисков по параметру (например, disk_size или disk_type)
    async def get_by_parameter(self, param, value):
        query = f"SELECT * FROM virtual_machines_disks WHERE {param} = $1"
        result = await self.conn.fetch(query, value)
        return result

    # Создание нового диска для виртуальной машины
    async def create(self, vm_id, disk_size, disk_type):
        created_at = datetime.utcnow()
        query = """
        INSERT INTO virtual_machines_disks (vm_id, disk_size, disk_type, created_at) 
        VALUES ($1, $2, $3, $4) 
        RETURNING id
        """
        result = await self.conn.fetchrow(query, vm_id, disk_size, disk_type, created_at)
        return result['id']
