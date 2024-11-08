from extensions import db
from datetime import datetime

class Request(db.Model):
    __tablename__ = 'requests'

    request_id = db.Column(db.String(50), primary_key = True)
    employee_id = db.Column(db.String(50), db.ForeignKey('employees.employee_id'), nullable = False)
    request_date = db.Column(db.DateTime, default = datetime.utcnow)
    request_status = db.Column(db.Enum('accept', 'reject', 'waiting', 'done'), nullable = False)

    request_lists = db.relationship('RequestList', backref='requests', lazy = True)

    def __repr__(self):
        return f'<Request {self.request_id}>'