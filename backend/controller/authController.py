from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
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

            # ส่ง JSON กลับมาเมื่อ login สำเร็จ
            return jsonify({"success": True, "message": "Login successful!", "role": user.role})

        else:
            # ส่ง JSON กลับมาเมื่อ login ล้มเหลว
            return jsonify({"success": False, "message": "Invalid username or password"})

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
