from extensions import db
from flask_login import UserMixin

class Employee(db.Model):
    __tablename__ = 'employees'
    employee_id = db.Column(db.String(50), primary_key=True)
    employee_fname = db.Column(db.String(50), nullable=False)
    employee_lname = db.Column(db.String(50), nullable=False)
    employee_age = db.Column(db.Integer, nullable=False)
    employee_sex = db.Column(db.String(5), nullable=False)
    employee_position = db.Column(db.Enum('worker', 'academic', 'clerical', 'keeper'), nullable=False)
    employee_address = db.Column(db.String(255), nullable=False)
    employee_salary = db.Column(db.Numeric(10, 2), nullable=False)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('worker', 'academic', 'clerical', 'keeper'), nullable=False)
    employee_id = db.Column(db.String(50), db.ForeignKey('employees.employee_id'), nullable=True)

    # ความสัมพันธ์ระหว่าง User และ Employee
    employee = db.relationship('Employee', backref='user', lazy=True)

    def get_id(self):
        return self.user_id
