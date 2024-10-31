CREATE DATABASE sa_farm_management;

USE sa_farm_management;

-- ตารางสำหรับเก็บข้อมูลพนักงาน
CREATE TABLE employees (
    employee_id VARCHAR(50) PRIMARY KEY,
    employee_fname VARCHAR(50) NOT NULL,
    employee_lname VARCHAR(50) NOT NULL,
    employee_age INT NOT NULL CHECK (employee_age > 0 AND employee_age < 120),
    employee_sex VARCHAR(10) NOT NULL,
    employee_position ENUM('worker', 'academic', 'clerical', 'keeper') NOT NULL,
    employee_address VARCHAR(255) NOT NULL,
    employee_salary DECIMAL(10, 2) NOT NULL,
    employee_image VARCHAR(255) NOT NULL
);

-- ตารางสำหรับเก็บข้อมูล user/password ของพนักงาน
CREATE TABLE users (
    user_id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    employee_id VARCHAR(50),

    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

-- ตารางสำหรับเก็บข้อมูลล็อตสินค้า
CREATE TABLE product_lists (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(50) NOT NULL,
    product_type ENUM('Food', 'Chemical') NOT NULL,
    threshold DECIMAL(10, 2) NOT NULL,
    product_image VARCHAR(255) NOT NULL
);

-- ตารางสำหรับเก็บข้อมูลล็อตสินค้า
CREATE TABLE product_lots (
    lot_id VARCHAR(50) PRIMARY KEY,
    lot_date DATETIME NOT NULL
);

-- ตารางสำหรับเก็บหน่วยสินค้า
CREATE TABLE unit (
    unit_id VARCHAR(50) PRIMARY KEY,
    product_type ENUM('Food', 'Chemical') NOT NULL,
    unit_name VARCHAR(50) NOT NULL
);

-- ตารางสำหรับเก็บข้อมูลสินค้า
CREATE TABLE products (
    product_id VARCHAR(50) NOT NULL,
    product_exp DATE NOT NULL,
    lot_id VARCHAR(50) NOT NULL,
    product_unit VARCHAR(50) NOT NULL,
    product_quantity DECIMAL(10, 2) NOT NULL,

    FOREIGN KEY (product_id) REFERENCES product_lists(product_id),
    FOREIGN KEY (lot_id) REFERENCES product_lots(lot_id),
    PRIMARY KEY (product_id, lot_id)  -- Composite Primary Key
);

-- ตารางสำหรับเก็บข้อมูลคำสั่งซื้อ
CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    order_date DATETIME NOT NULL,
    employee_id VARCHAR(50) NOT NULL,
    order_status VARCHAR(50) NOT NULL,

    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

-- ตารางสำหรับเก็บข้อมูลรายการคำสั่งซื้อ
CREATE TABLE order_lists (
    order_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    order_quantity DECIMAL(10, 2) NOT NULL,
    product_unit VARCHAR(50) NOT NULL,
    lot_id VARCHAR(50) NOT NULL,

    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES product_lists(product_id),
    FOREIGN KEY (lot_id) REFERENCES product_lots(lot_id),
    PRIMARY KEY (order_id, product_id)  -- Composite Primary Key
);

-- ตารางสำหรับเก็บข้อมูลคำขอเบิกสินค้า
CREATE TABLE requests (
    request_id VARCHAR(50) PRIMARY KEY,
    request_date DATETIME NOT NULL,
    employee_id VARCHAR(50) NOT NULL,
    request_status VARCHAR(50) NOT NULL,

    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

-- ตารางสำหรับเก็บข้อมูลรายการคำขอเบิกสินค้า
CREATE TABLE request_lists (
    request_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    request_quantity DECIMAL(10, 2) NOT NULL,
    product_unit VARCHAR(50) NOT NULL,

    FOREIGN KEY (request_id) REFERENCES requests(request_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    PRIMARY KEY (request_id, product_id)  -- Composite Primary Key
);

CREATE TABLE audit (
    audit_id VARCHAR(50) PRIMARY KEY,
    payment_due_date DATE NOT NULL,
    payment_status BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE audit_list (
    audit_list_id VARCHAR(50) PRIMARY KEY,
    audit_id VARCHAR(50) NOT NULL,
    order_id VARCHAR(50) NOT NULL,
    order_amount DECIMAL(10, 2) NOT NULL,

    FOREIGN KEY (audit_id) REFERENCES audit(audit_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

INSERT INTO employees (employee_id, employee_fname, employee_lname, employee_age, employee_sex, employee_position, employee_address, employee_salary, employee_image)
VALUES 
('E0001', 'เกียรติศักดิ์', 'สุขเกษม', 42, 'Male', 'keeper', '68 ซอยแจ้งวัฒนะ 13', 100000.00, 'https://img5.pic.in.th/file/secure-sv1/userd91ca9a3c145868a.png'),
('E0002', 'อนันต์', 'พรหมรักษ์', 50, 'Female', 'clerical', '5/10 ซอยพหลโยธิน 48', 55000.00, 'https://img5.pic.in.th/file/secure-sv1/userd91ca9a3c145868a.png'),
('E0003', 'ประภาศรี', 'ณรงค์ชัย', 33, 'Female', 'clerical', '28/7 ถนนพระราม 9', 48000.00, 'https://img5.pic.in.th/file/secure-sv1/userd91ca9a3c145868a.png'),
('E0004', 'สุชาติ', 'ศรีสมบูรณ์', 40, 'Male', 'clerical', '123/45 ถนนพญาไท', 60000.00, 'https://img5.pic.in.th/file/secure-sv1/userd91ca9a3c145868a.png'),
('E0005', 'สุนทร', 'อารีพร', 31, 'Male', 'worker', '109/3 ถนนนวมินทร์', 16000.00, 'https://img5.pic.in.th/file/secure-sv1/userd91ca9a3c145868a.png'),
('E0006', 'เกศรินทร์', 'สมบูรณ์สุข', 42, 'Female', 'worker', '456/7 หมู่ 9 ซอยลาดพร้าว 25', 16000.00, 'https://img5.pic.in.th/file/secure-sv1/userd91ca9a3c145868a.png'),
('E0007', 'สุนทร', 'เกียรติยศ', 42, 'Female', 'worker', '123/45 ถนนพญาไท', 15000.00, 'https://img5.pic.in.th/file/secure-sv1/userd91ca9a3c145868a.png'),
('E0008', 'ปรีดา', 'จารุวัฒน์', 39, 'Male', 'worker', '109/3 ถนนนวมินทร์', 16000.00, 'https://img5.pic.in.th/file/secure-sv1/userd91ca9a3c145868a.png'),
('E0009', 'เอกชัย', 'เกียรติยศ', 38, 'Male', 'worker', '109/3 ถนนนวมินทร์', 16000.00, 'https://img5.pic.in.th/file/secure-sv1/userd91ca9a3c145868a.png'),
('E0010', 'ดารินทร์', 'พรหมรักษ์', 50, 'Female', 'academic', '789/2 ถนนสุทธิสาร', 20000.00, 'https://img5.pic.in.th/file/secure-sv1/userd91ca9a3c145868a.png'),
('E0011', 'ประภาศรี', 'เพชรสุข', 35, 'Female', 'academic', '123 หมู่ 6 ตำบลหนองหาน', 20000.00, 'https://img5.pic.in.th/file/secure-sv1/userd91ca9a3c145868a.png'),
('E0012', 'ดวงใจ', 'แก้วเจริญ', 44, 'Male', 'academic', '50/10 หมู่ 2 ถนนงามวงศ์วาน', 21000.00, 'https://img5.pic.in.th/file/secure-sv1/userd91ca9a3c145868a.png');

INSERT INTO users (user_id, username, password, employee_id)
VALUES
('U1001', 'userE0001', 'ua(]!^k2M_D&', 'E0001'),
('U1002', 'userE0002', 'x>S{]ufDK!7`', 'E0002'),
('U1003', 'userE0003', 'x:<g8FTK+_Rq', 'E0003'),
('U1004', 'userE0004', 'n7LHG+xw/E)z', 'E0004'),
('U1005', 'userE0005', 's2MR#-FS^ec/', 'E0005'),
('U1006', 'userE0006', 'L7k!-vP%[Z>K', 'E0006'),
('U1007', 'userE0007', 'kgmQ`&[4nuPt', 'E0007'),
('U1008', 'userE0008', 'X)m"S!3x_C49', 'E0008'),
('U1009', 'userE0009', 'a%X[]<}2cp;f', 'E0009'),
('U1010', 'userE0010', 'C`M5xP&?v+K^', 'E0010'),
('U1011', 'userE0011', 'EH8_@yJGS!7-', 'E0011'),
('U1012', 'userE0012', 'pKWH%+43a&Jq', 'E0012');

INSERT INTO product_lists (product_id, product_name, product_type, threshold, product_image)
VALUES
('F001', 'Shrimp Food A', 'Food', 4000.0, 'https://img5.pic.in.th/file/secure-sv1/pet-food0808bd428320fded.png'),
('F002', 'Shrimp Food B', 'Food', 3000.0, 'https://img5.pic.in.th/file/secure-sv1/pet-food0808bd428320fded.png'),
('F003', 'Shrimp Food C', 'Food', 4000.0, 'https://img5.pic.in.th/file/secure-sv1/pet-food0808bd428320fded.png'),
('F004', 'Shrimp Food D', 'Food', 3000.0, 'https://img5.pic.in.th/file/secure-sv1/pet-food0808bd428320fded.png'),
('F005', 'Shrimp Food E', 'Food', 3000.0, 'https://img5.pic.in.th/file/secure-sv1/pet-food0808bd428320fded.png'),
('F006', 'Shrimp Food F', 'Food', 5000.0, 'https://img5.pic.in.th/file/secure-sv1/pet-food0808bd428320fded.png'),
('F007', 'Shrimp Food G', 'Food', 5000.0, 'https://img5.pic.in.th/file/secure-sv1/pet-food0808bd428320fded.png'),
('F008', 'Shrimp Food H', 'Food', 5000.0, 'https://img5.pic.in.th/file/secure-sv1/pet-food0808bd428320fded.png'),
('F009', 'Shrimp Food I', 'Food', 7000.0, 'https://img5.pic.in.th/file/secure-sv1/pet-food0808bd428320fded.png'),
('F010', 'Shrimp Food J', 'Food', 7000.0, 'https://img5.pic.in.th/file/secure-sv1/pet-food0808bd428320fded.png'),
('C001', 'Chemical S', 'Chemical', 1000.0, 'https://img2.pic.in.th/pic/chemistry.png'),
('C002', 'Chemical T', 'Chemical', 1000.0, 'https://img2.pic.in.th/pic/chemistry.png'),
('C003', 'Chemical U', 'Chemical', 1000.0, 'https://img2.pic.in.th/pic/chemistry.png'),
('C004', 'Chemical V', 'Chemical', 5000.0, 'https://img2.pic.in.th/pic/chemistry.png'),
('C005', 'Chemical W', 'Chemical', 5000.0, 'https://img2.pic.in.th/pic/chemistry.png'),
('C006', 'Chemical X', 'Chemical', 5000.0, 'https://img2.pic.in.th/pic/chemistry.png'),
('C007', 'Chemical Y', 'Chemical', 4000.0, 'https://img2.pic.in.th/pic/chemistry.png'),
('C008', 'Chemical Z', 'Chemical', 4000.0, 'https://img2.pic.in.th/pic/chemistry.png'),
('C009', 'Chemical Alpha', 'Chemical', 3000.0, 'https://img2.pic.in.th/pic/chemistry.png'),
('C010', 'Chemical Beta', 'Chemical', 3000.0, 'https://img2.pic.in.th/pic/chemistry.png');

INSERT INTO unit (unit_id, product_type, unit_name)
VALUES
('UNITF01', 'Food', 'kg'),
('UNITF02', 'Food', 'g'),
('UNITC01', 'Chemical', 'L'),
('UNITC02', 'Chemical', 'mL');

INSERT INTO product_lots (lot_id, lot_date)
VALUES
('LOT-20240128231548', '2026-10-10'),
('LOT-20240228233348', '2026-11-21'),
('LOT-20240328230912', '2026-12-28');

INSERT INTO products (product_id, product_exp, lot_id, product_unit, product_quantity)
VALUES 
('F001', '2026-10-10', 'LOT-20240128231548', 'kg', 500.00),
('F002', '2026-10-10', 'LOT-20240128231548', 'kg', 300.00),
('F003', '2026-10-10', 'LOT-20240128231548', 'kg', 400.00),
('F004', '2026-10-10', 'LOT-20240128231548', 'kg', 250.00),
('F005', '2026-10-10', 'LOT-20240128231548', 'kg', 600.00),
('F006', '2026-10-10', 'LOT-20240128231548', 'kg', 600.00),
('F007', '2026-10-10', 'LOT-20240128231548', 'kg', 600.00),
('F008', '2026-10-10', 'LOT-20240128231548', 'kg', 600.00),
('F009', '2026-10-10', 'LOT-20240128231548', 'kg', 600.00),
('F010', '2026-10-10', 'LOT-20240128231548', 'kg', 600.00),
('C001', '2026-10-10', 'LOT-20240128231548', 'L', 100.00),
('C002', '2026-10-10', 'LOT-20240128231548', 'L', 200.00),
('C003', '2026-10-10', 'LOT-20240128231548', 'L', 150.00),
('C004', '2026-10-10', 'LOT-20240128231548', 'L', 180.00),
('C005', '2026-10-10', 'LOT-20240128231548', 'L', 220.00),
('C006', '2026-10-10', 'LOT-20240128231548', 'L', 220.00),
('C007', '2026-10-10', 'LOT-20240128231548', 'L', 220.00),
('C008', '2026-10-10', 'LOT-20240128231548', 'L', 220.00),
('C009', '2026-10-10', 'LOT-20240128231548', 'L', 220.00),
('C010', '2026-10-10', 'LOT-20240128231548', 'L', 220.00),
('F001', '2026-11-21', 'LOT-20240228233348', 'kg', 500.00),
('F002', '2026-11-21', 'LOT-20240228233348', 'kg', 300.00),
('F003', '2026-11-21', 'LOT-20240228233348', 'kg', 400.00),
('F004', '2026-11-21', 'LOT-20240228233348', 'kg', 250.00),
('F005', '2026-11-21', 'LOT-20240228233348', 'kg', 600.00),
('F006', '2026-11-21', 'LOT-20240228233348', 'kg', 600.00),
('F007', '2026-11-21', 'LOT-20240228233348', 'kg', 600.00),
('F008', '2026-11-21', 'LOT-20240228233348', 'kg', 600.00),
('F009', '2026-11-21', 'LOT-20240228233348', 'kg', 600.00),
('F010', '2026-11-21', 'LOT-20240228233348', 'kg', 600.00),
('C001', '2026-11-21', 'LOT-20240228233348', 'L', 100.00),
('C002', '2026-11-21', 'LOT-20240228233348', 'L', 200.00),
('C003', '2026-11-21', 'LOT-20240228233348', 'L', 150.00),
('C004', '2026-11-21', 'LOT-20240228233348', 'L', 180.00),
('C005', '2026-11-21', 'LOT-20240228233348', 'L', 180.00),
('C006', '2026-11-21', 'LOT-20240228233348', 'L', 180.00),
('C007', '2026-11-21', 'LOT-20240228233348', 'L', 180.00),
('C008', '2026-11-21', 'LOT-20240228233348', 'L', 180.00),
('C009', '2026-11-21', 'LOT-20240228233348', 'L', 180.00),
('C010', '2026-11-21', 'LOT-20240228233348', 'L', 220.00),
('F001', '2026-12-28', 'LOT-20240328230912', 'kg', 100.00),
('F002', '2026-12-28', 'LOT-20240328230912', 'kg', 100.00),
('F003', '2026-12-28', 'LOT-20240328230912', 'kg', 100.00),
('F004', '2026-12-28', 'LOT-20240328230912', 'kg', 100.00),
('F005', '2026-12-28', 'LOT-20240328230912', 'kg', 100.00),
('F006', '2026-12-28', 'LOT-20240328230912', 'kg', 200.00),
('F007', '2026-12-28', 'LOT-20240328230912', 'kg', 200.00),
('F008', '2026-12-28', 'LOT-20240328230912', 'kg', 200.00),
('F009', '2026-12-28', 'LOT-20240328230912', 'kg', 200.00),
('F010', '2026-12-28', 'LOT-20240328230912', 'kg', 200.00),
('C001', '2026-12-28', 'LOT-20240328230912', 'L', 150.00),
('C002', '2026-12-28', 'LOT-20240328230912', 'L', 150.00),
('C003', '2026-12-28', 'LOT-20240328230912', 'L', 150.00),
('C004', '2026-12-28', 'LOT-20240328230912', 'L', 150.00),
('C005', '2026-12-28', 'LOT-20240328230912', 'L', 150.00),
('C006', '2026-12-28', 'LOT-20240328230912', 'L', 350.00),
('C007', '2026-12-28', 'LOT-20240328230912', 'L', 350.00),
('C008', '2026-12-28', 'LOT-20240328230912', 'L', 350.00),
('C009', '2026-12-28', 'LOT-20240328230912', 'L', 350.00),
('C010', '2026-12-28', 'LOT-20240328230912', 'L', 350.00);

INSERT INTO orders (order_id, order_date, employee_id, order_status) 
VALUES
('ORD-20241031234150', '2024-10-31 23:41:50', 'E0001', 'accept'),
('ORD-20241031234216', '2024-10-31 23:42:16', 'E0001', 'accept'),
('ORD-20241031234247', '2024-10-31 23:42:47', 'E0001', 'accept'),
('ORD-20241031234303', '2024-10-31 23:43:03', 'E0001', 'accept'),
('ORD-20241031234318', '2024-10-31 23:43:18', 'E0001', 'accept'),
('ORD-20241031234409', '2024-10-31 23:44:09', 'E0001', 'accept'),
('ORD-20241031234423', '2024-10-31 23:44:23', 'E0001', 'accept');

INSERT INTO order_lists (order_id, product_id, order_quantity, product_unit, lot_id) 
VALUES
('ORD-20241031234150', 'C001', 10.00, 'L', 'LOT-20240128231548'),
('ORD-20241031234150', 'C002', 10.00, 'L', 'LOT-20240128231548'),
('ORD-20241031234150', 'C003', 10.00, 'L', 'LOT-20240128231548'),
('ORD-20241031234150', 'C004', 10.00, 'L', 'LOT-20240128231548'),
('ORD-20241031234216', 'C005', 20.00, 'L', 'LOT-20240128231548'),
('ORD-20241031234216', 'C006', 20.00, 'L', 'LOT-20240128231548'),
('ORD-20241031234216', 'C007', 20.00, 'L', 'LOT-20240128231548'),
('ORD-20241031234216', 'C008', 20.00, 'L', 'LOT-20240128231548'),
('ORD-20241031234247', 'C001', 10.00, 'L', 'LOT-20240128231548'),
('ORD-20241031234247', 'F001', 10.00, 'kg', 'LOT-20240128231548'),
('ORD-20241031234303', 'C006', 10.00, 'L', 'LOT-20240128231548'),
('ORD-20241031234303', 'F002', 10.00, 'kg', 'LOT-20240128231548'),
('ORD-20241031234318', 'C003', 20.00, 'L', 'LOT-20240228233348'),
('ORD-20241031234318', 'F003', 20.00, 'kg', 'LOT-20240228233348'),
('ORD-20241031234409', 'C004', 40.00, 'L', 'LOT-20240228233348'),
('ORD-20241031234409', 'F004', 40.00, 'kg', 'LOT-20240228233348'),
('ORD-20241031234423', 'C005', 10.00, 'L', 'LOT-20240228233348'),
('ORD-20241031234423', 'F005', 10.00, 'kg', 'LOT-20240228233348');

INSERT INTO audit (audit_id, payment_due_date, payment_status) 
VALUES
('AUD-20241031234539', '2025-01-09', 1),
('AUD-20241031234603', '2025-03-09', 1),
('AUD-20241031234622', '2025-05-09', 1);

INSERT INTO audit_list (audit_list_id, audit_id, order_id, order_amount) 
VALUES
('AL-ORD-20241031234150', 'AUD-20241031234539', 'ORD-20241031234150', 100000.00),
('AL-ORD-20241031234216', 'AUD-20241031234539', 'ORD-20241031234216', 127000.00),
('AL-ORD-20241031234247', 'AUD-20241031234603', 'ORD-20241031234247', 110000.00),
('AL-ORD-20241031234303', 'AUD-20241031234603', 'ORD-20241031234303', 136000.00),
('AL-ORD-20241031234318', 'AUD-20241031234622', 'ORD-20241031234318', 110100.00),
('AL-ORD-20241031234409', 'AUD-20241031234622', 'ORD-20241031234409', 120320.00),
('AL-ORD-20241031234423', 'AUD-20241031234622', 'ORD-20241031234423', 123000.00);

INSERT INTO requests (request_id, request_date, employee_id, request_status) 
VALUES
('REQ-20241031235435', '2024-10-31 23:54:35', 'E0007', 'waiting'),
('REQ-20241031235501', '2024-10-31 23:55:01', 'E0007', 'waiting'),
('REQ-20241031235556', '2024-10-31 23:55:56', 'E0012', 'waiting'),
('REQ-20241031235719', '2024-10-31 23:57:19', 'E0012', 'waiting'),
('REQ-20241031235817', '2024-10-31 23:58:17', 'E0011', 'waiting'),
('REQ-20241031235843', '2024-10-31 23:58:43', 'E0010', 'waiting'),
('REQ-20241031235924', '2024-10-31 23:59:24', 'E0009', 'waiting');

INSERT INTO request_lists (request_id, product_id, request_quantity, product_unit) 
VALUES
('REQ-20241031235435', 'F001', 1.00, 'kg'),
('REQ-20241031235435', 'F002', 1.00, 'kg'),
('REQ-20241031235435', 'F004', 1.00, 'kg'),
('REQ-20241031235435', 'F005', 1.00, 'kg'),
('REQ-20241031235501', 'F001', 1.00, 'kg'),
('REQ-20241031235501', 'F003', 1.00, 'kg'),
('REQ-20241031235501', 'F005', 1.00, 'kg'),
('REQ-20241031235556', 'C001', 1.00, 'L'),
('REQ-20241031235556', 'C002', 1.00, 'L'),
('REQ-20241031235556', 'C003', 1.00, 'L'),
('REQ-20241031235556', 'C004', 1.00, 'L'),
('REQ-20241031235556', 'C005', 1.00, 'L'),
('REQ-20241031235719', 'C001', 3.00, 'L'),
('REQ-20241031235719', 'C002', 3.00, 'L'),
('REQ-20241031235719', 'C003', 3.00, 'L'),
('REQ-20241031235719', 'C004', 3.00, 'L'),
('REQ-20241031235719', 'C005', 3.00, 'L'),
('REQ-20241031235817', 'C001', 4.00, 'L'),
('REQ-20241031235817', 'C002', 4.00, 'L'),
('REQ-20241031235817', 'C003', 4.00, 'L'),
('REQ-20241031235817', 'C004', 4.00, 'L'),
('REQ-20241031235817', 'C005', 4.00, 'L'),
('REQ-20241031235843', 'C001', 2.00, 'L'),
('REQ-20241031235843', 'C002', 2.00, 'L'),
('REQ-20241031235843', 'C003', 2.00, 'L'),
('REQ-20241031235843', 'C004', 2.00, 'L'),
('REQ-20241031235843', 'C005', 2.00, 'L'),
('REQ-20241031235924', 'F001', 6.00, 'kg'),
('REQ-20241031235924', 'F002', 6.00, 'kg'),
('REQ-20241031235924', 'F003', 6.00, 'kg'),
('REQ-20241031235924', 'F004', 6.00, 'kg'),
('REQ-20241031235924', 'F005', 6.00, 'kg');