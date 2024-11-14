from extensions import db

class ProductList(db.Model):
    __tablename__ = 'product_lists'
    product_id = db.Column(db.String(50), primary_key=True)
    product_name = db.Column(db.String(50), nullable=False)
    product_type = db.Column(db.Enum('Food', 'Chemical'), nullable=False)
    threshold = db.Column(db.Numeric(20, 3), nullable=False)
    product_image = db.Column(db.String(255), nullable=False)
