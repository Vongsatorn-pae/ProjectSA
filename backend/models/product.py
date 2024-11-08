from extensions import db

class Product(db.Model):
    __tablename__ = 'products'

    product_id = db.Column(db.String(50), primary_key = True)
    product_name = db.Column(db.String(50), nullable = False)
    product_type = db.Column(db.Enum('Food', 'Chemical'), nullable = False)
    product_unit = db.Column(db.String(50), nullable = False)
    product_quantity = db.Column(db.DECIMAL(10, 3), nullable = False)
    threshold = db.Column(db.DECIMAL(10, 3), nullable = False)
    product_image = db.Column(db.String(255), nullable = False)
