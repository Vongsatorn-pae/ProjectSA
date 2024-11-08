from extensions import db
from flask_login import UserMixin

class Employee(db.Model):
    __tablename__ = 'employees'

    employee_id = db.Column(db.String(50), primary_key = True)
    employee_fname = db.Column(db.String(50), nullable = False)
    employee_lname = db.Column(db.String(50), nullable = False)
    employee_age = db.Column(db.Integer, nullable = False)
    employee_sex = db.Column(db.String(10), nullable = False)
    employee_position = db.Column(db.Enum('worker', 'academic', 'clerical', 'keeper'), nullable = False)
    employee_address = db.Column(db.String(255), nullable = False)
    employee_salary = db.Column(db.DECIMAL(10, 3), nullable = False)
    employee_image = db.Column(db.String(255), nullable = False)
    username = db.Column(db.String(255), nullable = False, unique = True)
    password = db.Column(db.String(255), nullable = False)

    # ฟังก์ชันที่ Flask-Login ต้องการ
    @property
    def is_active(self):
        """True, as all users are active."""
        return True
    
    def get_id(self):
        """Return the employee_id to satisfy Flask-Login's requirements."""
        return str(self.employee_id)

    @property
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True

    @property
    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False
