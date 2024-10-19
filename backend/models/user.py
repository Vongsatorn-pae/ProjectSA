from models.employee import Employee
from extensions import db
from flask_login import UserMixin  # นำเข้า UserMixin สำหรับการทำงานร่วมกับ Flask-Login

class User(db.Model, UserMixin):  # สืบทอด UserMixin เพื่อใช้งานแอตทริบิวต์ที่จำเป็น
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.employee_id'))
    employee = db.relationship('Employee', backref='user')

    # ฟังก์ชันที่ Flask-Login ต้องการ
    @property
    def is_active(self):
        """True, as all users are active."""
        return True

    @property
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True

    @property
    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def get_id(self):
        """Return the user_id to satisfy Flask-Login's requirements."""
        return str(self.user_id)
