import random
import string
from flask import Blueprint, render_template, redirect, session, url_for, request, flash, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from models.employee import Employee
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
def load_user(employee_id):
    return Employee.query.get(employee_id)

@authController.route('/', methods=['GET', 'POST'])

# Route สำหรับหน้า login
@authController.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # ตรวจสอบผู้ใช้ในฐานข้อมูล
        employee = Employee.query.filter_by(username = username).first()
        
        if employee and employee.password == password:
            login_user(employee)

            # ส่ง JSON กลับมาเมื่อ login สำเร็จ โดยใช้ employee.employee_position แทน role
            return jsonify({"success": True, "message": "Login successful!", "employee_position": employee.employee_position})

        else:
            # ส่ง JSON กลับมาเมื่อ login ล้มเหลว
            return jsonify({"success": False, "message": "Invalid username or password"})

    return render_template('auth/login.html')

@authController.route('/logout')
@login_required
def logout():
    # ล้าง cart ใน session
    session.pop('cart', None)
    
    # ทำการ logout ผู้ใช้
    logout_user()
    return redirect(url_for('auth.login'))

# Route สำหรับ create account
@authController.route('/create_account', methods=['GET', 'POST'])
@login_required
def create_account():
    if current_user.employee_position != 'keeper':  # ตรวจสอบว่าเป็น Keeper เท่านั้น
        # flash('You do not have permission to access this page.', 'danger')
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
        existing_user = Employee.query.filter_by(username=username).first()
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
            employee_position = employee_position,
            employee_address = employee_address,
            employee_salary = employee_salary,
            employee_image = 'https://kasets.art/u1LfNp',
            username=username,
            password=password
        )
        db.session.add(new_employee)
        db.session.commit()  # บันทึกพนักงานใหม่เข้าสู่ฐานข้อมูล

        # สร้าง User ใหม่
        # new_user = User(
        #     user_id = generate_user_id(),
        #     username = username,
        #     password = password,
        #     employee_id = new_employee.employee_id  # เชื่อมกับพนักงานที่เพิ่งสร้าง
        # )
        # db.session.add(new_user)
        # db.session.commit()  # บันทึกผู้ใช้ใหม่เข้าสู่ฐานข้อมูล

        flash(f'Account created successfully! Username: {username}, Password: {password}', 'success')
        return redirect(url_for('main.keeper_dashboard'))

    return render_template('auth/create_account.html')

@authController.route('/profile')
@login_required
def view_profile():
    employee = current_user
    return render_template('profile.html', employee=employee)

@authController.route('/auth/change_password', methods=['GET', 'POST'])
@login_required
def change_password_page():
    if request.method == 'GET':
        return render_template('auth/change_password.html')
    
    if request.method == 'POST':
        # การจัดการ POST (การอัปเดตรหัสผ่าน) - ตัวอย่างการตอบกลับ
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        # ตัวอย่างการตรวจสอบข้อมูลรหัสผ่าน
        if current_password != current_user.password:
            return jsonify({"status": "error", "message": "Current password is incorrect"}), 400
        if new_password != confirm_password:
            return jsonify({"status": "error", "message": "New passwords do not match"}), 400
        if len(new_password) < 8:
            return jsonify({"status": "error", "message": "Password must be at least 8 characters"}), 400

        # การบันทึกรหัสผ่านใหม่
        try:
            current_user.password = new_password
            db.session.commit()
            return jsonify({"status": "success", "message": "Password updated successfully"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "message": "Failed to update password"}), 500
    
@authController.route('/auth/edit_address', methods=['GET', 'POST'])
@login_required
def edit_address():
    if request.method == 'POST':
        data = request.get_json()
        new_address = data.get('address')

        if not new_address:
            return jsonify({"status": "error", "message": "Address is required"}), 400

        try:
            current_user.employee_address = new_address
            db.session.commit()
            flash('Address updated successfully', 'success')
            return jsonify({"status": "success"}), 200
        except Exception as e:
            db.session.rollback()
            flash('Failed to update address', 'danger')
            return jsonify({"status": "error", "message": str(e)}), 400
    return render_template('auth/edit_address.html')
    
@authController.route('/employees', methods=['GET'])
@login_required
def view_employees():
    try:
        employees = Employee.query.all()  # ดึงข้อมูลพนักงานทั้งหมดจากฐานข้อมูล
        return render_template('keeper/all_employee.html', employees=employees)
    except Exception as e:
        flash(f"Error fetching employees: {str(e)}", "danger")
        return redirect(url_for('main.index'))
    
@authController.route('/employees/<string:employee_id>', methods=['GET'])
@login_required
def view_employee_detail(employee_id):
    try:
        employee = Employee.query.get_or_404(employee_id)  # ดึงข้อมูลพนักงานตาม employee_id
        return render_template('keeper/employee_detail.html', employee=employee)
    except Exception as e:
        flash(f"Error fetching employee details: {str(e)}", "danger")
        return redirect(url_for('auth.view_employees'))
