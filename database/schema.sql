CREATE DATABASE sa_farm_management;

USE sa_farm_management;

-- ตารางสำหรับเก็บข้อมูลพนักงาน
CREATE TABLE employees (
    employee_id VARCHAR(50) PRIMARY KEY,
    employee_fname VARCHAR(50) NOT NULL,
    employee_lname VARCHAR(50) NOT NULL,
    employee_age INT NOT NULL CHECK (employee_age > 0 AND employee_age < 120),
    employee_sex VARCHAR(5) NOT NULL,
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
    lot_date DATE NOT NULL
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
    order_date DATE NOT NULL,
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
    request_date DATE NOT NULL,
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
    audit_id INT PRIMARY KEY,
    payment_due_date DATE NOT NULL,
    payment_status BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE audit_list (
    audit_list_id INT PRIMARY KEY,
    audit_id INT NOT NULL,
    order_id VARCHAR(50) NOT NULL,
    order_amount DECIMAL(10, 2) NOT NULL,

    FOREIGN KEY (audit_id) REFERENCES audit(audit_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

INSERT INTO employees (employee_id, employee_fname, employee_lname, employee_age, employee_sex, employee_position, employee_address, employee_salary, employee_image)
VALUES 
('E001', 'John', 'Doe', 30, 'M', 'worker', '123 Main St', 50000.00, 'https://img5.pic.in.th/file/secure-sv1/userd91ca9a3c145868a.png'),
('E002', 'Jane', 'Smith', 28, 'F', 'academic', '456 Oak Ave', 55000.00, 'https://img5.pic.in.th/file/secure-sv1/userd91ca9a3c145868a.png'),
('E003', 'Michael', 'Johnson', 35, 'M', 'clerical', '789 Pine Rd', 48000.00, 'https://img5.pic.in.th/file/secure-sv1/userd91ca9a3c145868a.png'),
('E004', 'Emily', 'Davis', 40, 'F', 'keeper', '321 Cedar St', 60000.00, 'https://img5.pic.in.th/file/secure-sv1/userd91ca9a3c145868a.png');

INSERT INTO users (user_id, username, password, employee_id)
VALUES 
('U001', 'john_doe', 'hashedpassword1','E001'),
('U002', 'jane_smith', 'hashedpassword2', 'E002'),
('U003', 'michael_johnson', 'hashedpassword3', 'E003'),
('U004', 'emily_davis', 'hashedpassword4','E004');

INSERT INTO product_lists (product_id, product_name, product_type, threshold, product_image)
VALUES
('F001', 'Shrimp Food A', 'Food', 2000.0, 'https://img5.pic.in.th/file/secure-sv1/pet-food0808bd428320fded.png'),
('F002', 'Shrimp Food B', 'Food', 2000.0, 'https://img5.pic.in.th/file/secure-sv1/pet-food0808bd428320fded.png'),
('F003', 'Shrimp Food C', 'Food', 2000.0, 'https://img5.pic.in.th/file/secure-sv1/pet-food0808bd428320fded.png'),
('F004', 'Shrimp Food D', 'Food', 2000.0, 'https://img5.pic.in.th/file/secure-sv1/pet-food0808bd428320fded.png'),
('F005', 'Shrimp Food E', 'Food', 2000.0, 'https://img5.pic.in.th/file/secure-sv1/pet-food0808bd428320fded.png'),
('C001', 'Chemical X', 'Chemical', 2000.0, 'https://img2.pic.in.th/pic/chemistry.png'),
('C002', 'Chemical Y', 'Chemical', 2000.0, 'https://img2.pic.in.th/pic/chemistry.png'),
('C003', 'Chemical Z', 'Chemical', 2000.0, 'https://img2.pic.in.th/pic/chemistry.png'),
('C004', 'Chemical Alpha', 'Chemical', 2000.0, 'https://img2.pic.in.th/pic/chemistry.png'),
('C005', 'Chemical Beta', 'Chemical', 2000.0, 'https://img2.pic.in.th/pic/chemistry.png');

INSERT INTO product_lots (lot_id, lot_date)
VALUES
('LOT001', '2024-10-10'),
('LOT002', '2024-11-10');

INSERT INTO unit (unit_id, product_type, unit_name)
VALUES
('UNITF01', 'Food', 'kg'),
('UNITF02', 'Food', 'g'),
('UNITC01', 'Chemical', 'L'),
('UNITC02', 'Chemical', 'mL');

INSERT INTO products (product_id, product_exp, lot_id, product_unit, product_quantity)
VALUES 
('F001', '2024-10-10', 'LOT001', 'kg', 500.00),
('F002', '2024-10-10', 'LOT001', 'kg', 300.00),
('F003', '2024-10-10', 'LOT001', 'kg', 400.00),
('F004', '2024-10-10', 'LOT001', 'kg', 250.00),
('F005', '2024-10-10', 'LOT001', 'kg', 600.00),
('C001', '2024-10-10', 'LOT001', 'L', 100.00),
('C002', '2024-10-10', 'LOT001', 'L', 200.00),
('C003', '2024-10-10', 'LOT001', 'L', 150.00),
('C004', '2024-10-10', 'LOT001', 'L', 180.00),
('C005', '2024-10-10', 'LOT001', 'L', 220.00),
('F001', '2024-11-10', 'LOT002', 'kg', 500.00),
('F002', '2024-11-10', 'LOT002', 'kg', 300.00),
('F003', '2024-11-10', 'LOT002', 'kg', 400.00),
('F004', '2024-11-10', 'LOT002', 'kg', 250.00),
('F005', '2024-11-10', 'LOT002', 'kg', 600.00),
('C001', '2024-11-10', 'LOT002', 'L', 100.00),
('C002', '2024-11-10', 'LOT002', 'L', 200.00),
('C003', '2024-11-10', 'LOT002', 'L', 150.00),
('C004', '2024-11-10', 'LOT002', 'L', 180.00),
('C005', '2024-11-10', 'LOT002', 'L', 220.00);
