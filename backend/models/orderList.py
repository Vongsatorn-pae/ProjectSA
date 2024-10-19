from extensions import db

# โมเดลสำหรับตาราง order_lists
class OrderList(db.Model):
    __tablename__ = 'order_lists'
    order_id = db.Column(db.String(50), db.ForeignKey('orders.order_id'), primary_key=True)  # รหัสคำสั่งซื้อ (Foreign Key)
    product_id = db.Column(db.String(50), db.ForeignKey('product_lists.product_id'), primary_key=True)  # รหัสสินค้า (Foreign Key)
    product_quantity = db.Column(db.Float, nullable=False)  # จำนวนที่สั่งซื้อ
    product_unit = db.Column(db.String(50), nullable=False)  # หน่วยของสินค้า
    lot_id = db.Column(db.String(50), db.ForeignKey('product_lots.lot_id'), nullable=False)  # รหัสล็อตสินค้า (Foreign Key)

    # ความสัมพันธ์กับ ProductList (สินค้า) และ ProductLot (ล็อตสินค้า)
    product = db.relationship('ProductList', backref='order_lists', lazy=True)
    lot = db.relationship('ProductLot', backref='order_lists', lazy=True)
