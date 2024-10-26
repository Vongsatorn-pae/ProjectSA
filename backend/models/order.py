from extensions import db
from datetime import datetime

# โมเดลสำหรับคำสั่งซื้อ (Order)
class Order(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.String(50), primary_key=True)  # Primary Key สำหรับคำสั่งซื้อ
    order_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)  # วันที่ทำการสั่งซื้อ
    employee_id = db.Column(db.String(50), db.ForeignKey('employees.employee_id'), nullable=False)  # เชื่อมโยงกับตาราง employees
    order_status = db.Column(db.Enum('accept', 'reject', 'waiting'), nullable=False)  # สถานะของคำสั่งซื้อ

    # ความสัมพันธ์กับ OrderList (รายการคำสั่งซื้อ)
    order_lists = db.relationship('OrderList', backref='order', lazy=True)
    audit_lists = db.relationship('AuditList', backref='order_reference', lazy=True, overlaps="order")

    def __repr__(self):
        return f'<Order {self.order_id}>'
