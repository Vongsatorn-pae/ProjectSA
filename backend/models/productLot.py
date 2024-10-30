from extensions import db
from datetime import datetime

class ProductLot(db.Model):
    __tablename__ = 'product_lots'
    lot_id = db.Column(db.String(50), primary_key=True)
    lot_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
