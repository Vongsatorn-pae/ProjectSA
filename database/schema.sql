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
    employee_salary DECIMAL(10, 2) NOT NULL
);

-- ตารางสำหรับเก็บข้อมูล user/password ของพนักงาน
CREATE TABLE users (
    user_id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('worker', 'academic', 'clerical', 'keeper') NOT NULL,  -- คนงาน(worker), นักวิชาการ(academic), ธุรการ(clerical), ผู้ดูแล(keeper)
    employee_id VARCHAR(50),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

-- ตารางสำหรับเก็บข้อมูลล็อตสินค้า
CREATE TABLE product_lists (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(50) NOT NULL,
    product_type VARCHAR(50) NOT NULL,
    threshold DECIMAL(10, 2) NOT NULL
);

-- ตารางสำหรับเก็บข้อมูลล็อตสินค้า
CREATE TABLE product_lots (
    lot_id VARCHAR(50) PRIMARY KEY,
    lot_date DATE NOT NULL
);

-- ตารางสำหรับเก็บข้อมูลสินค้า
CREATE TABLE products (
    product_id VARCHAR(50) NOT NULL,
    product_name VARCHAR(50) NOT NULL,
    product_type VARCHAR(50) NOT NULL,
    product_exp DATE NOT NULL,
    lot_id VARCHAR(50) NOT NULL,
    product_unit VARCHAR(50) NOT NULL,
    product_quantity DECIMAL(10, 2) NOT NULL,

    FOREIGN KEY (product_id) REFERENCES product_lists(product_id),
    FOREIGN KEY (lot_id) REFERENCES product_lots(lot_id),
    PRIMARY KEY (product_id, lot_id)  -- Composite Primary Key
    -- FOREIGN KEY (product_unit) REFERENCES order_lists(),
    -- FOREIGN KEY (product_quantity) REFERENCES order_lists()
);

-- ตารางสำหรับเก็บข้อมูลคำสั่งซื้อ
CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    order_date DATE NOT NULL,
    employee_id VARCHAR(50) NOT NULL,
    order_status BOOLEAN NOT NULL,

    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

-- ตารางสำหรับเก็บข้อมูลรายการคำสั่งซื้อ
CREATE TABLE order_lists (
    -- order_list_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    product_quantity DECIMAL(10, 2) NOT NULL,
    product_unit VARCHAR(50) NOT NULL,
    lot_id VARCHAR(50) NOT NULL,

    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (lot_id) REFERENCES product_lots(lot_id)
);

-- ตารางสำหรับเก็บข้อมูลคำขอเบิกสินค้า
CREATE TABLE requests (
    request_id VARCHAR(50) PRIMARY KEY,
    request_date DATE NOT NULL,
    request_status BOOLEAN NOT NULL,
    employee_id VARCHAR(50) NOT NULL,

    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

-- ตารางสำหรับเก็บข้อมูลรายการคำขอเบิกสินค้า
CREATE TABLE request_lists (
    request_list_id VARCHAR(50) PRIMARY KEY,
    request_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    request_quantity DECIMAL(10, 2) NOT NULL,

    FOREIGN KEY (request_id) REFERENCES requests(request_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

INSERT INTO employees (employee_id, employee_fname, employee_lname, employee_age, employee_sex, employee_position, employee_address, employee_salary)
VALUES 
('E001', 'John', 'Doe', 30, 'M', 'worker', '123 Main St', 50000.00),
('E002', 'Jane', 'Smith', 28, 'F', 'academic', '456 Oak Ave', 55000.00),
('E003', 'Michael', 'Johnson', 35, 'M', 'clerical', '789 Pine Rd', 48000.00),
('E004', 'Emily', 'Davis', 40, 'F', 'keeper', '321 Cedar St', 60000.00);

INSERT INTO users (user_id, username, password, role, employee_id)
VALUES 
('U001', 'john_doe', 'hashedpassword1', 'worker', 'E001'),
('U002', 'jane_smith', 'hashedpassword2', 'academic', 'E002'),
('U003', 'michael_johnson', 'hashedpassword3', 'clerical', 'E003'),
('U004', 'emily_davis', 'hashedpassword4', 'keeper', 'E004');

INSERT INTO product_lists (product_id, product_name, product_type, threshold)
VALUES
('F001', 'Shrimp Food A', 'อาหาร', 10.0),
('F002', 'Shrimp Food B', 'อาหาร', 10.0),
('F003', 'Shrimp Food C', 'อาหาร', 10.0),
('F004', 'Shrimp Food D', 'อาหาร', 10.0),
('F005', 'Shrimp Food E', 'อาหาร', 10.0),
('C001', 'Chemical X', 'สารเคมี', 10.0),
('C002', 'Chemical Y', 'สารเคมี', 10.0),
('C003', 'Chemical Z', 'สารเคมี', 10.0),
('C004', 'Chemical Alpha', 'สารเคมี', 10.0),
('C005', 'Chemical Beta', 'สารเคมี', 10.0);

INSERT INTO product_lots (lot_id, lot_date)
VALUES
('LOT001', '2024-10-10'),
('LOT002', '2024-11-10');

INSERT INTO products (product_id, product_name, product_type, product_exp, lot_id, product_unit, product_quantity)
VALUES 
('F001', 'Shrimp Food A', 'อาหาร', '2024-10-10', 'LOT001', 'kg', 500.00),
('F002', 'Shrimp Food B', 'อาหาร', '2024-10-10', 'LOT001', 'kg', 300.00),
('F003', 'Shrimp Food C', 'อาหาร', '2024-10-10', 'LOT001', 'kg', 400.00),
('F004', 'Shrimp Food D', 'อาหาร', '2024-10-10', 'LOT001', 'kg', 250.00),
('F005', 'Shrimp Food E', 'อาหาร', '2024-10-10', 'LOT001', 'kg', 600.00),
('C001', 'Chemical X', 'สารเคมี', '2024-10-10', 'LOT001', 'liter', 100.00),
('C002', 'Chemical Y', 'สารเคมี', '2024-10-10', 'LOT001', 'liter', 200.00),
('C003', 'Chemical Z', 'สารเคมี', '2024-10-10', 'LOT001', 'liter', 150.00),
('C004', 'Chemical Alpha', 'สารเคมี', '2024-10-10', 'LOT001', 'liter', 180.00),
('C005', 'Chemical Beta', 'สารเคมี', '2024-10-10', 'LOT001', 'liter', 220.00),
('F001', 'Shrimp Food A', 'อาหาร', '2024-11-10', 'LOT002', 'kg', 500.00),
('F002', 'Shrimp Food B', 'อาหาร', '2024-11-10', 'LOT002', 'kg', 300.00),
('F003', 'Shrimp Food C', 'อาหาร', '2024-11-10', 'LOT002', 'kg', 400.00),
('F004', 'Shrimp Food D', 'อาหาร', '2024-11-10', 'LOT002', 'kg', 250.00),
('F005', 'Shrimp Food E', 'อาหาร', '2024-11-10', 'LOT002', 'kg', 600.00),
('C001', 'Chemical X', 'สารเคมี', '2024-11-10', 'LOT002', 'liter', 100.00),
('C002', 'Chemical Y', 'สารเคมี', '2024-11-10', 'LOT002', 'liter', 200.00),
('C003', 'Chemical Z', 'สารเคมี', '2024-11-10', 'LOT002', 'liter', 150.00),
('C004', 'Chemical Alpha', 'สารเคมี', '2024-11-10', 'LOT002', 'liter', 180.00),
('C005', 'Chemical Beta', 'สารเคมี', '2024-11-10', 'LOT002', 'liter', 220.00);
