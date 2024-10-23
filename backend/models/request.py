from extensions import db
from datetime import datetime

class Request(db.Model):
    __tablename__ = 'requests'
    request_id = db.Column(db.Integer, primary_key=True)
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    employee_id = db.Column(db.String(20), db.ForeignKey('employees.employee_id'), nullable=False)
    request_status = db.Column(db.Boolean, default=False)  # False = Pending, True = Approved

    # สัมพันธ์กับ RequestList (หนึ่งคำขอเบิกมีหลายรายการสินค้า)
    request_lists = db.relationship('RequestList', backref='request', lazy=True)

    def __repr__(self):
        return f'<Request {self.request_id}>'