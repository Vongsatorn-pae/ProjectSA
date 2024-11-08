from extensions import db
from datetime import datetime

class Audit(db.Model):
    __tablename__ = 'audits'

    audit_id = db.Column(db.String(50), primary_key = True)
    payment_due_date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    payment_status = db.Column(db.Boolean, nullable = False, default = False)

    audit_list = db.relationship("AuditList", back_populates = "audit")
