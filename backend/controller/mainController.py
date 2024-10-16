from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user

mainController = Blueprint('main', __name__)

# หน้าแดชบอร์ดของผู้ดูแล (keeper)
@mainController.route('/keeper_dashboard')
@login_required
def keeper_dashboard():
    if current_user.role != 'keeper':
        return abort(403)  # ปฏิเสธการเข้าถึงถ้า role ไม่ใช่ 'keeper'
    return render_template('keeper/dashboard.html')

# หน้าแดชบอร์ดของนักวิชาการ (academic)
@mainController.route('/academic_dashboard')
@login_required
def academic_dashboard():
    if current_user.role != 'academic':
        return abort(403)
    return render_template('academic/dashboard.html')

# หน้าแดชบอร์ดของคนงาน (worker)
@mainController.route('/worker_dashboard')
@login_required
def worker_dashboard():
    if current_user.role != 'worker':
        return abort(403)
    return render_template('worker/dashboard.html')

# หน้าแดชบอร์ดของธุรการ (clerical)
@mainController.route('/clerical_dashboard')
@login_required
def clerical_dashboard():
    if current_user.role != 'clerical':
        return abort(403)
    return render_template('clerical/dashboard.html')
