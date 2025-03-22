-- table for VM
CREATE TABLE IF NOT EXISTS virtual_machines (
    id SERIAL PRIMARY KEY,
    ram_size INT NOT NULL,
    cpu_count INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- table for disks
CREATE TABLE IF NOT EXISTS virtual_machines_disks (
    id SERIAL PRIMARY KEY,
    vm_id INT REFERENCES virtual_machines(id) ON DELETE CASCADE,
    disk_size INT NOT NULL,
    disk_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- index for searching of VM by ID
CREATE INDEX IF NOT EXISTS idx_vm_id ON virtual_machines_disks (vm_id);
