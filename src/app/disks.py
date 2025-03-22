import asyncpg
from datetime import datetime

class VirtualMachineDisk:
    def __init__(self, conn):
        self.conn = conn

    async def list(self):
        """list of disks """
        
        query = """
        SELECT 
            vmd.id AS disk_id,
            vmd.disk_size,
            vm.id AS vm_id,
            vm.ram_size,
            vm.cpu_count
        FROM 
            virtual_machines_disks vmd
        JOIN 
            virtual_machines vm ON vmd.vm_id = vm.id;
        """
        result = await self.conn.fetch(query)
        return result

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

    # Обновление диска для виртуальной машины
    async def update(self, disk_id, disk_size=None, disk_type=None):
        updated_at = datetime.utcnow()
        query = """
        UPDATE virtual_machines_disks
        SET disk_size = COALESCE($2, disk_size), 
            disk_type = COALESCE($3, disk_type), 
            created_at = $4
        WHERE id = $1
        """
        await self.conn.execute(query, disk_id, disk_size, disk_type, updated_at)
        return True
