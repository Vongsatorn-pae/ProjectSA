import random
import string
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from models.user import Employee, User
from extensions import db, login_manager


authController = Blueprint('auth', __name__)

# ฟังก์ชันสำหรับสร้าง employee_id สุ่ม
def generate_employee_id():
    random_id = random.randint(1000, 9999)  # สุ่มเลขระหว่าง 1000 ถึง 9999
    return f"E{random_id}"  # ใส่ตัวอักษร "E" นำหน้า

# ฟังก์ชันสำหรับสร้าง user_id สุ่ม
def generate_user_id():
    random_id = random.randint(1000, 9999)  # สุ่มเลขระหว่าง 1000 ถึง 9999
    return f"U{random_id}"  # ใส่ตัวอักษร "E" นำหน้า

# ฟังก์ชันสำหรับสร้าง password สุ่ม
def generate_random_password(length = 8):
    letters = string.ascii_letters
    digits = string.digits
    return ''.join(random.choice(letters + digits) for i in range(length))

# โหลดผู้ใช้โดยใช้ user_id
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@authController.route('/', methods=['GET', 'POST'])

# Route สำหรับหน้า login
@authController.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # ตรวจสอบผู้ใช้ในฐานข้อมูล
        user = User.query.filter_by(username = username).first()
        
        if user and user.password == password:
            login_user(user)

            # ส่ง JSON กลับมาเมื่อ login สำเร็จ โดยใช้ employee.employee_position แทน role
            return jsonify({"success": True, "message": "Login successful!", "employee_position": user.employee.employee_position})

        else:
            # ส่ง JSON กลับมาเมื่อ login ล้มเหลว
            return jsonify({"success": False, "message": "Invalid username or password"})

    return render_template('auth/login.html')

# Route สำหรับ logout
@authController.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# Route สำหรับ create account
@authController.route('/create_account', methods=['GET', 'POST'])
@login_required
def create_account():
    if current_user.employee.employee_position != 'keeper':  # ตรวจสอบว่าเป็น Keeper เท่านั้น
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # รับค่าจากฟอร์ม (ถ้าไม่กรอกใช้ค่าเริ่มต้น)
        employee_id = request.form.get('employee_id') or generate_employee_id()
        username = request.form.get('employee_id') or f'user{employee_id}'
        password = request.form.get('employee_id') or generate_random_password()

        # รับรายละเอียดพนักงานใหม่
        employee_fname = request.form['employee_fname']
        employee_lname = request.form['employee_lname']
        employee_age = request.form['employee_age'] if request.form['employee_age'] else 'Unknown'
        employee_sex = request.form['employee_sex'] if request.form['employee_sex'] else 'Unknown'
        employee_position = request.form['employee_position']  # ตรวจสอบตำแหน่งจากฟอร์ม
        employee_address = request.form['employee_address'] if request.form['employee_address'] else 'Unknown'
        employee_salary = request.form['employee_salary']

        # ตรวจสอบว่ามี username นี้ในระบบแล้วหรือไม่
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('auth.create_account'))

        # สร้าง Employee ใหม่
        new_employee = Employee(
            employee_id = employee_id,
            employee_fname = employee_fname,
            employee_lname = employee_lname,
            employee_age = employee_age,
            employee_sex = employee_sex,
            employee_position = employee_position,  # ใช้ตำแหน่งที่รับจากฟอร์ม
            employee_address = employee_address,
            employee_salary = employee_salary,
            employee_image = 'https://img5.pic.in.th/file/secure-sv1/userd91ca9a3c145868a.png'
        )
        db.session.add(new_employee)
        db.session.commit()  # บันทึกพนักงานใหม่เข้าสู่ฐานข้อมูล

        # สร้าง User ใหม่
        new_user = User(
            user_id = generate_user_id(),
            username = username,
            password = password,
            employee_id = new_employee.employee_id  # เชื่อมกับพนักงานที่เพิ่งสร้าง
        )
        db.session.add(new_user)
        db.session.commit()  # บันทึกผู้ใช้ใหม่เข้าสู่ฐานข้อมูล

        flash(f'Account created successfully! Username: {username}, Password: {password}', 'success')
        return redirect(url_for('main.keeper_dashboard'))

    return render_template('auth/create_account.html')

@authController.route('/profile')
@login_required
def view_profile():
    employee = current_user.employee
    return render_template('profile.html', employee=employee)
