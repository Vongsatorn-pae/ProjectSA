from extensions import db

class Unit(db.Model):
    __tablename__ = 'unit'
    unit_id = db.Column(db.String(50), primary_key=True)
    product_type = db.Column(db.Enum('Food', 'Chemical'), nullable=False)
    unit_name = db.Column(db.String(50), nullable=False)