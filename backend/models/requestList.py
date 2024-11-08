from extensions import db

class RequestList(db.Model):
    __tablename__ = 'request_lists'

    request_list_id = db.Column(db.String(20), primary_key = True)
    request_id = db.Column(db.String(50), db.ForeignKey('requests.request_id'), nullable = False)
    product_id = db.Column(db.String(50), db.ForeignKey('product_lists.product_id'), nullable = False)
    unit_id = db.Column(db.String(50), db.ForeignKey('units.unit_id'), nullable = False)
    request_quantity = db.Column(db.DECIMAL(10, 3), nullable = False)

    # product = db.relationship('ProductList', backref='request_lists')

    # def __repr__(self):
    #     return f'<RequestList {self.request_list_id} - Product {self.product_id}>'
