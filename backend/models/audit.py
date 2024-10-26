from extensions import db
from datetime import datetime

class Audit(db.Model):
    __tablename__ = 'audit'
    audit_id = db.Column(db.String(50), primary_key=True)
    payment_due_date = db.Column(db.Date, nullable=False)
    payment_status = db.Column(db.Boolean, nullable=False, default=True)

    # สร้างความสัมพันธ์กับ audit_list
    audit_lists = db.relationship("AuditList", back_populates="audit")
