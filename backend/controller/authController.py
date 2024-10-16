from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from models.user import User
from extensions import db, login_manager

authController = Blueprint('auth', __name__)

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
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            # ตรวจสอบ role ของผู้ใช้และเปลี่ยนเส้นทางไปยังหน้าที่สอดคล้อง
            if user.role == 'keeper':
                return redirect(url_for('main.keeper_dashboard'))
            elif user.role == 'academic':
                return redirect(url_for('main.academic_dashboard'))
            elif user.role == 'worker':
                return redirect(url_for('main.worker_dashboard'))
            elif user.role == 'clerical':
                return redirect(url_for('main.clerical_dashboard'))
            else:
                flash('Role not recognized.', 'danger')
                return redirect(url_for('auth.login'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

# Route สำหรับ logout
@authController.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# Route สำหรับ register
@authController.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # สร้างผู้ใช้ใหม่
        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash('User registered successfully', 'success')
        return redirect(url_for('main.index'))

    return render_template('register.html')
