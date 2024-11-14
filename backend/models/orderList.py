from extensions import db

class OrderList(db.Model):
    __tablename__ = 'order_lists'

    order_list_id = db.Column(db.String(50), primary_key = True)
    order_id = db.Column(db.String(50), db.ForeignKey('orders.order_id'), nullable = False)
    product_id = db.Column(db.String(50), db.ForeignKey('products.product_id'), nullable = False)
    unit_id = db.Column(db.String(50), db.ForeignKey('units.unit_id'), nullable = False)
    order_quantity = db.Column(db.DECIMAL(20, 3), nullable = False)

    # product = db.relationship('Product', backref = 'order_lists', lazy = True)
    # lot = db.relationship('ProductLot', backref = 'order_lists', lazy = True)
    