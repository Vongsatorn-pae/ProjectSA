from extensions import db

class Product(db.Model):
    __tablename__ = 'products'
    product_id = db.Column(db.String(50), db.ForeignKey('product_lists.product_id'), primary_key=True)
    product_exp = db.Column(db.Date, nullable=False)
    lot_id = db.Column(db.String(50), db.ForeignKey('product_lots.lot_id'), primary_key=True)
    product_unit = db.Column(db.String(50), nullable=False)
    product_quantity = db.Column(db.Numeric(10, 2), nullable=False)
