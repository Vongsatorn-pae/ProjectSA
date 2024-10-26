from extensions import db

class AuditList(db.Model):
    __tablename__ = 'audit_list'
    audit_list_id = db.Column(db.String(50), primary_key=True)
    audit_id = db.Column(db.String(50), db.ForeignKey('audit.audit_id'), nullable=False)
    order_id = db.Column(db.String(50), db.ForeignKey('orders.order_id'), nullable=False)
    order_amount = db.Column(db.DECIMAL(10, 2), nullable=False)

    # กำหนดความสัมพันธ์ระหว่าง Audit และ Orders
    audit = db.relationship("Audit", back_populates="audit_lists")
    order = db.relationship("Order", back_populates="audit_lists", overlaps="order_reference")
