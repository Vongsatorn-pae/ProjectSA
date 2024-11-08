from extensions import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'

    order_id = db.Column(db.String(50), primary_key = True)
    employee_id = db.Column(db.String(50), db.ForeignKey('employees.employee_id'), nullable = False)
    order_date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    order_status = db.Column(db.Enum('accept', 'reject', 'waiting', 'done'), nullable = False)

    order_lists = db.relationship('OrderList', backref = 'orders', lazy = True)
    audit_lists = db.relationship('AuditList', backref = 'order_reference', lazy = True, overlaps = "order")

    def __repr__(self):
        return f'<Order {self.order_id}>'
