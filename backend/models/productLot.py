from extensions import db
from datetime import datetime, timedelta

def default_exp():
    return datetime.utcnow() + timedelta(days=365*2)

class ProductLot(db.Model):
    __tablename__ = 'product_lots'

    lot_id = db.Column(db.String(50), primary_key = True)
    product_id = db.Column(db.String(50), db.ForeignKey('products.product_id'), nullable = False)
    lot_date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    lot_exp = db.Column(db.DateTime, nullable = False, default = default_exp)
    lot_quantity = db.Column(db.DECIMAL(20, 3), nullable = False)

    # products = db.relationship('Product', backref = 'product_lots', lazy = True)
