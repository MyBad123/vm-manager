-- table for VM
CREATE TABLE IF NOT EXISTS virtual_machines (
    id SERIAL PRIMARY KEY,
    ram_size INT NOT NULL,
    cpu_count INT NOT NULL
);

-- table for disks of VM
CREATE TABLE IF NOT EXISTS virtual_machines_disks (
    id SERIAL PRIMARY KEY,
    vm_id INT NOT NULL,
    disk_size INT NOT NULL,
    FOREIGN KEY (vm_id) REFERENCES virtual_machines(id) ON DELETE CASCADE
);

-- table for credentials of VM
CREATE TABLE IF NOT EXISTS virtual_machine_credentials (
    id SERIAL PRIMARY KEY,
    vm_id INT NOT NULL,
    login VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    last_login TIMESTAMP DEFAULT NULL,
    FOREIGN KEY (vm_id) REFERENCES virtual_machines(id) ON DELETE CASCADE
);


-- index for searching of VM by ID
CREATE INDEX IF NOT EXISTS idx_vm_id ON virtual_machines_disks (vm_id);
