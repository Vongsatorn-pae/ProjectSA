CREATE DATABASE sa_farm_management;

USE sa_farm_management;

CREATE TABLE employees (
    employee_id VARCHAR(50) PRIMARY KEY,
    employee_fname VARCHAR(50) NOT NULL,
    employee_lname VARCHAR(50) NOT NULL,
    employee_age INT NOT NULL CHECK (employee_age > 0 AND employee_age < 120),
    employee_sex VARCHAR(10) NOT NULL,
    employee_position ENUM('worker', 'academic', 'clerical', 'keeper') NOT NULL,
    employee_address VARCHAR(255) NOT NULL,
    employee_salary DECIMAL(10, 3) NOT NULL,
    employee_image VARCHAR(255) NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(50) NOT NULL,
    product_type ENUM('Food', 'Chemical') NOT NULL,
    product_unit VARCHAR(50) NOT NULL,
    product_quantity DECIMAL(10, 3) NOT NULL,
    threshold DECIMAL(10, 3) NOT NULL,
    product_image VARCHAR(255) NOT NULL
);

CREATE TABLE product_lots (
    lot_id VARCHAR(50) PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL,
    lot_date DATETIME NOT NULL,
    lot_exp DATETIME NOT NULL,
    lot_quantity DECIMAL(10, 3) NOT NULL,

    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE units (
    unit_id VARCHAR(50) PRIMARY KEY,
    product_type ENUM('Food', 'Chemical') NOT NULL,
    unit_name VARCHAR(50) NOT NULL
);

CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL,
    order_date DATETIME NOT NULL,
    order_status ENUM('waiting', 'accept', 'reject', 'done') NOT NULL,

    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE order_lists (
    order_list_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    unit_id VARCHAR(50) NOT NULL,
    order_quantity DECIMAL(10, 3) NOT NULL,

    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (unit_id) REFERENCES units(unit_id)
);

CREATE TABLE requests (
    request_id VARCHAR(50) PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL,
    request_date DATETIME NOT NULL,
    request_status ENUM('waiting', 'accept', 'reject', 'done') NOT NULL,

    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE request_lists (
    request_list_id VARCHAR(50) PRIMARY KEY,
    request_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    unit_id VARCHAR(50) NOT NULL,
    request_quantity DECIMAL(10, 3) NOT NULL,

    FOREIGN KEY (request_id) REFERENCES requests(request_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (unit_id) REFERENCES units(unit_id)
);

CREATE TABLE audits (
    audit_id VARCHAR(50) PRIMARY KEY,
    payment_due_date DATETIME NOT NULL,
    payment_status BOOLEAN NOT NULL
);

CREATE TABLE audit_lists (
    audit_list_id VARCHAR(50) PRIMARY KEY,
    audit_id VARCHAR(50) NOT NULL,
    order_id VARCHAR(50) NOT NULL,
    order_amount DECIMAL(10, 3) NOT NULL,

    FOREIGN KEY (audit_id) REFERENCES audits(audit_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

INSERT INTO employees (employee_id, employee_fname, employee_lname, employee_age, employee_sex, employee_position, employee_address, employee_salary, employee_image, username, password)
VALUES 
('E0001', 'เกียรติศักดิ์', 'สุขเกษม', 42, 'Male', 'keeper', '68 ซอยแจ้งวัฒนะ 13', 100000.000, 'https://kasets.art/u1LfNp', 'userE0001', 'A6zmXp3Z'),
('E0002', 'อนันต์', 'พรหมรักษ์', 50, 'Female', 'clerical', '5/10 ซอยพหลโยธิน 48', 55000.000, 'https://kasets.art/u1LfNp', 'userE0002', 'sqHGC4fZ'),
('E0003', 'ประภาศรี', 'ณรงค์ชัย', 33, 'Female', 'clerical', '28/7 ถนนพระราม 9', 48000.000, 'https://kasets.art/u1LfNp', 'userE0003', 'ZRxDz9aK'),
('E0004', 'สุชาติ', 'ศรีสมบูรณ์', 40, 'Male', 'clerical', '123/45 ถนนพญาไท', 60000.000, 'https://kasets.art/u1LfNp', 'userE0004', 'aw64BU5u'),
('E0005', 'สุนทร', 'อารีพร', 31, 'Male', 'worker', '109/3 ถนนนวมินทร์', 16000.000, 'https://kasets.art/u1LfNp', 'userE0005', 'U3nDbRL4'),
('E0006', 'เกศรินทร์', 'สมบูรณ์สุข', 42, 'Female', 'worker', '456/7 หมู่ 9 ซอยลาดพร้าว 25', 16000.000, 'https://kasets.art/u1LfNp', 'userE0006', 'Re5fW3uk'),
('E0007', 'สุนทร', 'เกียรติยศ', 42, 'Female', 'worker', '123/45 ถนนพญาไท', 15000.000, 'https://kasets.art/u1LfNp', 'userE0007', 'fm4EbCZ3'),
('E0008', 'ปรีดา', 'จารุวัฒน์', 39, 'Male', 'worker', '109/3 ถนนนวมินทร์', 16000.000, 'https://kasets.art/u1LfNp', 'userE0008', 'Ey6mV8Yf'),
('E0009', 'เอกชัย', 'เกียรติยศ', 38, 'Male', 'worker', '109/3 ถนนนวมินทร์', 16000.000, 'https://kasets.art/u1LfNp', 'userE0009', 'cGuC3qPf'),
('E0010', 'ดารินทร์', 'พรหมรักษ์', 50, 'Female', 'academic', '789/2 ถนนสุทธิสาร', 20000.000, 'https://kasets.art/u1LfNp', 'userE0010', 'xJs32QNY'),
('E0011', 'ประภาศรี', 'เพชรสุข', 35, 'Female', 'academic', '123 หมู่ 6 ตำบลหนองหาน', 20000.000, 'https://kasets.art/u1LfNp', 'userE0011', 'h8A63Zdn'),
('E0012', 'ดวงใจ', 'แก้วเจริญ', 44, 'Male', 'academic', '50/10 หมู่ 2 ถนนงามวงศ์วาน', 21000.000, 'https://kasets.art/u1LfNp', 'userE0012', 'D3Yh2ycT');

INSERT INTO products (product_id, product_name, product_type, product_unit, product_quantity, threshold, product_image)
VALUES
('F001', 'Shrimp Food A', 'Food', 'Kg', 1.200, 2000.000, 'https://kasets.art/51kGYq'),
('F002', 'Shrimp Food B', 'Food', 'Kg', 3000.000, 2500.000, 'https://kasets.art/51kGYq'),
('F003', 'Shrimp Food C', 'Food', 'Kg', 2.300, 2500.000, 'https://kasets.art/51kGYq'),
('F004', 'Shrimp Food D', 'Food', 'Kg', 3000.000, 3500.000, 'https://kasets.art/51kGYq'),
('F005', 'Shrimp Food E', 'Food', 'Kg', 3000.000, 3000.000, 'https://kasets.art/51kGYq'),
('F006', 'Shrimp Food F', 'Food', 'Kg', 5000.000, 3000.000, 'https://kasets.art/51kGYq'),
('F007', 'Shrimp Food G', 'Food', 'Kg', 5000.000, 4500.000, 'https://kasets.art/51kGYq'),
('F008', 'Shrimp Food H', 'Food', 'Kg', 5000.000, 2000.000, 'https://kasets.art/51kGYq'),
('F009', 'Shrimp Food I', 'Food', 'Kg', 7000.000, 2000.000, 'https://kasets.art/51kGYq'),
('F010', 'Shrimp Food J', 'Food', 'Kg', 7000.000, 2000.000, 'https://kasets.art/51kGYq'),
('C001', 'Chemical S', 'Chemical', 'L', 3000.000, 3000.000, 'https://kasets.art/HtBpeI'),
('C002', 'Chemical T', 'Chemical', 'L', 1600.000, 2000.000, 'https://kasets.art/HtBpeI'),
('C003', 'Chemical U', 'Chemical', 'L', 1900.000, 3000.000, 'https://kasets.art/HtBpeI'),
('C004', 'Chemical V', 'Chemical', 'L', 4.700, 5000.000, 'https://kasets.art/HtBpeI'),
('C005', 'Chemical W', 'Chemical', 'L', 2.100, 5000.000, 'https://kasets.art/HtBpeI'),
('C006', 'Chemical X', 'Chemical', 'L', 5000.000, 4000.000, 'https://kasets.art/HtBpeI'),
('C007', 'Chemical Y', 'Chemical', 'L', 4000.000, 4000.000, 'https://kasets.art/HtBpeI'),
('C008', 'Chemical Z', 'Chemical', 'L', 1000.000, 2000.000, 'https://kasets.art/HtBpeI'),
('C009', 'Chemical Alpha', 'Chemical', 'L', 3000.000, 2000.000, 'https://kasets.art/HtBpeI'),
('C010', 'Chemical Beta', 'Chemical', 'L', 3000.000, 2000.000, 'https://kasets.art/HtBpeI');

INSERT INTO product_lots (lot_id, product_id, lot_date, lot_exp, lot_quantity)
VALUES
('LOT-20240128231541-1', 'F001', '2024-03-28 00:00:00', '2026-01-20 00:00:00', 4000.000),
('LOT-20240228233312-1', 'C010', '2024-03-28 00:00:00', '2026-01-20 00:00:00', 3000.000),
('LOT-20240228233322-1', 'F002', '2024-03-28 00:00:00', '2026-01-20 00:00:00', 3000.000),
('LOT-20240228233333-1', 'F003', '2024-03-28 00:00:00', '2026-01-20 00:00:00', 4000.000),
('LOT-20240228233341-1', 'C009', '2024-03-28 00:00:00', '2026-01-20 00:00:00', 3000.000),
('LOT-20240228233342-1', 'C001', '2024-03-28 00:00:00', '2026-01-20 00:00:00', 3000.000),
('LOT-20240228233343-1', 'C002', '2024-03-28 00:00:00', '2026-01-20 00:00:00', 1600.000),
('LOT-20240228233344-1', 'C003', '2024-03-28 00:00:00', '2026-01-20 00:00:00', 1900.000),
('LOT-20240228233345-1', 'C004', '2024-03-28 00:00:00', '2026-01-20 00:00:00', 5000.000),
('LOT-20240228233346-1', 'C005', '2024-03-28 00:00:00', '2026-01-20 00:00:00', 5000.000),
('LOT-20240228233347-1', 'C006', '2024-03-28 00:00:00', '2026-01-20 00:00:00', 5000.000),
('LOT-20240228233348-1', 'C007', '2024-03-28 00:00:00', '2026-01-20 00:00:00', 4000.000),
('LOT-20240228233349-1', 'C008', '2024-03-28 00:00:00', '2026-01-20 00:00:00', 1000.000),
('LOT-20240228233354-1', 'F004', '2024-03-28 00:00:00', '2026-01-20 00:00:00', 3000.000),
('LOT-20240328230911-1', 'F010', '2024-03-28 00:00:00', '2026-01-20 00:00:00', 7000.000),
('LOT-20240328230915-1', 'F005', '2024-03-28 00:00:00', '2026-01-20 00:00:00', 3000.000),
('LOT-20240328230916-1', 'F006', '2024-03-28 00:00:00', '2026-01-20 00:00:00', 5000.000),
('LOT-20240328230917-1', 'F007', '2024-03-28 00:00:00', '2026-01-20 00:00:00', 5000.000),
('LOT-20240328230918-1', 'F008', '2024-03-28 00:00:00', '2026-01-20 00:00:00', 5000.000),
('LOT-20240328230919-1', 'F009', '2024-03-28 00:00:00', '2026-01-20 00:00:00', 7000.000),
('LOT-20241112193659-1', 'C004', '2024-11-12 19:36:59', '2026-11-12 12:36:59', 2.000),
('LOT-20241112193700-2', 'F001', '2024-11-12 19:37:00', '2026-11-12 12:37:00', 2.000);

INSERT INTO units (unit_id, product_type, unit_name)
VALUES
('UNITF01', 'Food', 'Kg'),
('UNITF02', 'Food', 'g'),
('UNITC01', 'Chemical', 'L'),
('UNITC02', 'Chemical', 'mL');

INSERT INTO orders (order_id, employee_id, order_date, order_status) 
VALUES
('ORD-20241031234150', 'E0001', '2024-10-31 23:41:50', 'done'),
('ORD-20241031234216', 'E0001', '2024-10-31 23:42:16', 'done'),
('ORD-20241031234247', 'E0001', '2024-10-31 23:42:47', 'done'),
('ORD-20241031234303', 'E0001', '2024-10-31 23:43:03', 'done'),
('ORD-20241031234318', 'E0001', '2024-10-31 23:43:18', 'done'),
('ORD-20241031234409', 'E0001', '2024-10-31 23:44:09', 'done'),
('ORD-20241031234423', 'E0001', '2024-10-31 23:44:23', 'done'),
('ORD-20241112193319', 'E0001', '2024-11-12 19:33:19', 'done'),
('ORD-20241112193328', 'E0001', '2024-11-12 19:33:28', 'waiting');

INSERT INTO order_lists (order_list_id, order_id, product_id, unit_id, order_quantity) 
VALUES
('ORDL-20241031234151-1', 'ORD-20241031234150', 'F001', 'UNITF01', 10.000),
('ORDL-20241031234152-2', 'ORD-20241031234150', 'F002', 'UNITF01', 10.000),
('ORDL-20241031234153-3', 'ORD-20241031234150', 'C001', 'UNITC01', 10.000),
('ORDL-20241031234154-4', 'ORD-20241031234150', 'C002', 'UNITC01', 10.000),
('ORDL-20241031234215-1', 'ORD-20241031234216', 'F001', 'UNITF01', 20.000),
('ORDL-20241031234216-2', 'ORD-20241031234216', 'F002', 'UNITF01', 20.000),
('ORDL-20241031234217-3', 'ORD-20241031234216', 'C001', 'UNITC01', 20.000),
('ORDL-20241031234218-4', 'ORD-20241031234216', 'C002', 'UNITC01', 20.000),
('ORDL-20241031234241-1', 'ORD-20241031234247', 'C003', 'UNITC01', 10.000),
('ORDL-20241031234249-2', 'ORD-20241031234247', 'F003', 'UNITF01', 10.000),
('ORDL-20241031234302-1', 'ORD-20241031234303', 'F004', 'UNITF01', 10.000),
('ORDL-20241031234303-2', 'ORD-20241031234303', 'C004', 'UNITC01', 10.000),
('ORDL-20241031234314-1', 'ORD-20241031234318', 'F005', 'UNITF01', 20.000),
('ORDL-20241031234315-2', 'ORD-20241031234318', 'C005', 'UNITC01', 20.000),
('ORDL-20241031234406-1', 'ORD-20241031234409', 'F006', 'UNITF01', 40.000),
('ORDL-20241031234407-2', 'ORD-20241031234409', 'C006', 'UNITC01', 40.000),
('ORDL-20241031234428-1', 'ORD-20241031234423', 'F007', 'UNITF01', 10.000),
('ORDL-20241031234429-2', 'ORD-20241031234423', 'C007', 'UNITC01', 10.000),
('ORDL-20241112193319-1', 'ORD-20241112193319', 'C004', 'UNITC01', 2.000),
('ORDL-20241112193319-2', 'ORD-20241112193319', 'F001', 'UNITF01', 2.000),
('ORDL-20241112193328-1', 'ORD-20241112193328', 'C005', 'UNITC01', 1.000),
('ORDL-20241112193328-2', 'ORD-20241112193328', 'F003', 'UNITF01', 1.000);

INSERT INTO requests (request_id, employee_id, request_date, request_status) 
VALUES
('REQ-20241031235435', 'E0007', '2024-10-31 23:54:35', 'done'),
('REQ-20241031235501', 'E0007', '2024-10-31 23:55:01', 'reject'),
('REQ-20241031235556', 'E0012', '2024-10-31 23:55:56', 'done'),
('REQ-20241031235719', 'E0012', '2024-10-31 23:57:19', 'reject'),
('REQ-20241031235817', 'E0011', '2024-10-31 23:58:17', 'done'),
('REQ-20241031235843', 'E0010', '2024-10-31 23:58:43', 'waiting'),
('REQ-20241031235924', 'E0009', '2024-10-31 23:59:24', 'waiting'),
('REQ-20241112193447', 'E0011', '2024-11-12 19:34:47', 'waiting');

INSERT INTO request_lists (request_list_id, request_id, product_id, unit_id, request_quantity) 
VALUES
('REQL-20241031235411-2', 'REQ-20241031235556', 'C003', 'UNITC01', 1.000),
('REQL-20241031235412-3', 'REQ-20241031235556', 'C004', 'UNITC01', 1.000),
('REQL-20241031235413-4', 'REQ-20241031235556', 'C005', 'UNITC01', 1.000),
('REQL-20241031235414-5', 'REQ-20241031235719', 'C001', 'UNITC01', 3.000),
('REQL-20241031235415-1', 'REQ-20241031235719', 'C002', 'UNITC01', 3.000),
('REQL-20241031235416-2', 'REQ-20241031235719', 'C003', 'UNITC01', 3.000),
('REQL-20241031235417-3', 'REQ-20241031235719', 'C004', 'UNITC01', 3.000),
('REQL-20241031235418-4', 'REQ-20241031235719', 'C005', 'UNITC01', 3.000),
('REQL-20241031235419-1', 'REQ-20241031235817', 'C001', 'UNITC01', 4.000),
('REQL-20241031235421-2', 'REQ-20241031235817', 'C002', 'UNITC01', 4.000),
('REQL-20241031235422-3', 'REQ-20241031235817', 'C003', 'UNITC01', 4.000),
('REQL-20241031235423-4', 'REQ-20241031235817', 'C004', 'UNITC01', 4.000),
('REQL-20241031235424-5', 'REQ-20241031235817', 'C005', 'UNITC01', 4.000),
('REQL-20241031235425-5', 'REQ-20241031235843', 'C001', 'UNITC01', 2.000),
('REQL-20241031235426-1', 'REQ-20241031235843', 'C002', 'UNITC01', 2.000),
('REQL-20241031235427-2', 'REQ-20241031235843', 'C003', 'UNITC01', 2.000),
('REQL-20241031235428-3', 'REQ-20241031235843', 'C004', 'UNITC01', 2.000),
('REQL-20241031235429-4', 'REQ-20241031235843', 'C005', 'UNITC01', 2.000),
('REQL-20241031235431-1', 'REQ-20241031235435', 'F001', 'UNITF01', 1.000),
('REQL-20241031235432-2', 'REQ-20241031235435', 'F002', 'UNITF01', 1.000),
('REQL-20241031235433-3', 'REQ-20241031235435', 'F004', 'UNITF01', 1.000),
('REQL-20241031235434-4', 'REQ-20241031235435', 'F005', 'UNITF01', 1.000),
('REQL-20241031235435-1', 'REQ-20241031235501', 'F001', 'UNITF01', 1.000),
('REQL-20241031235436-2', 'REQ-20241031235501', 'F003', 'UNITF01', 1.000),
('REQL-20241031235437-3', 'REQ-20241031235501', 'F005', 'UNITF01', 1.000),
('REQL-20241031235441-5', 'REQ-20241031235924', 'F001', 'UNITF01', 6.000),
('REQL-20241031235442-1', 'REQ-20241031235924', 'F002', 'UNITF01', 6.000),
('REQL-20241031235453-2', 'REQ-20241031235924', 'F003', 'UNITF01', 6.000),
('REQL-20241031235454-3', 'REQ-20241031235924', 'F004', 'UNITF01', 6.000),
('REQL-20241031235455-4', 'REQ-20241031235924', 'F005', 'UNITF01', 6.000),
('REQL-20241031235556-1', 'REQ-20241031235556', 'C002', 'UNITC01', 1.000),
('REQL-20241112193447-1', 'REQ-20241112193447', 'C001', 'UNITC02', 200.000),
('REQL-20241112193447-2', 'REQ-20241112193447', 'C004', 'UNITC02', 200.000),
('REQL-20241112193447-3', 'REQ-20241112193447', 'C008', 'UNITC02', 300.000);

INSERT INTO audits (audit_id, payment_due_date, payment_status) 
VALUES
('AUD-20241031234539', '2024-01-09 00:00:00', 1),
('AUD-20241031234603', '2024-03-09 00:00:00', 1),
('AUD-20241031234622', '2024-05-09 00:00:00', 1),
('AUD-20241112193709', '2025-01-21 19:37:09', 0);

INSERT INTO audit_lists (audit_list_id, audit_id, order_id, order_amount) 
VALUES
('AL-ORD-20241031234150', 'AUD-20241031234539', 'ORD-20241031234150', 100000.000),
('AL-ORD-20241031234216', 'AUD-20241031234539', 'ORD-20241031234216', 127000.000),
('AL-ORD-20241031234247', 'AUD-20241031234603', 'ORD-20241031234247', 110000.000),
('AL-ORD-20241031234303', 'AUD-20241031234603', 'ORD-20241031234303', 136000.000),
('AL-ORD-20241031234318', 'AUD-20241031234622', 'ORD-20241031234318', 110100.000),
('AL-ORD-20241031234409', 'AUD-20241031234622', 'ORD-20241031234409', 120320.000),
('AL-ORD-20241031234423', 'AUD-20241031234622', 'ORD-20241031234423', 123000.000),
('AL-ORD-20241112193319', 'AUD-20241112193709', 'ORD-20241112193319', 1000000.000);