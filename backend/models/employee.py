from extensions import db

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
    employee_image = db.Column(db.String(255), nullable=False)
