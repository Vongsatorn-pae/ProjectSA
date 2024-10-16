from extensions import db

class ProductLot(db.Model):
    __tablename__ = 'product_lots'
    lot_id = db.Column(db.String(50), primary_key=True)
    lot_date = db.Column(db.Date, nullable=False)
