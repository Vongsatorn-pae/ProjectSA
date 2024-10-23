from extensions import db

class RequestList(db.Model):
    __tablename__ = 'request_lists'
    request_id = db.Column(db.Integer, db.ForeignKey('requests.request_id'), primary_key=True)
    product_id = db.Column(db.String(20), db.ForeignKey('product_lists.product_id'), primary_key=True)
    request_quantity = db.Column(db.Integer, nullable=False)
    product_unit = db.Column(db.String(50), nullable=False)

    # สัมพันธ์กับ ProductList (รายการสินค้าจาก product_lists)
    product = db.relationship('ProductList', backref='request_lists')

    def __repr__(self):
        return f'<RequestList {self.request_list_id} - Product {self.product_id}>'