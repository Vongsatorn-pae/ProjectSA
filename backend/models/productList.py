from extensions import db

class ProductList(db.Model):
    __tablename__ = 'product_lists'
    product_id = db.Column(db.String(50), primary_key=True)
    product_name = db.Column(db.String(50), nullable=False)
    product_type = db.Column(db.String(50), nullable=False)
    threshold = db.Column(db.Numeric(10, 2), nullable=False)
