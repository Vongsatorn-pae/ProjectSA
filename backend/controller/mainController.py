from flask import Blueprint, flash, redirect, render_template, abort, request, url_for
from flask_login import logout_user, login_required, current_user
from controller.orderController import order_history
from controller.stockController import stock_alert
from models.order import Order
from models.product import Product
from models.productList import ProductList
from models.request import Request
from models.requestList import RequestList
from extensions import db
from controller.stockController import stock_alert
from controller.stockController import get_stock_alerts

mainController = Blueprint('main', __name__)

@mainController.route('/index', methods=['GET'])
@login_required
def index():
    # Log out user
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('auth.login'))

@mainController.route('/keeper_dashboard')
@login_required
def keeper_dashboard():
    if current_user.employee_position != 'keeper':
        return abort(403)

    # ดึงข้อมูล order ที่สถานะเป็น accept (จำกัด 3 รายการ) และเรียงจากใหม่ล่าสุด
    accepted_orders = db.session.query(Order).filter_by(order_status='accept').order_by(Order.order_date.desc()).limit(3).all()

    # ดึงข้อมูล stock alert (จำกัด 3 รายการ)
    stock_alerts = get_stock_alerts(limit=3)

    return render_template(
        'keeper/dashboard.html', 
        accepted_orders=accepted_orders, 
        stock_alerts=stock_alerts
    )

# หน้าแดชบอร์ดของนักวิชาการ (academic)
@mainController.route('/academic_dashboard')
@login_required
def academic_dashboard():
    if current_user.employee_position != 'academic':
        return abort(403)
    return render_template('academic/dashboard.html')

# หน้าแดชบอร์ดของคนงาน (worker)
@mainController.route('/worker_dashboard')
@login_required
def worker_dashboard():
    if current_user.employee_position != 'worker':
        return abort(403)
    return render_template('worker/dashboard.html')

# หน้าแดชบอร์ดของธุรการ (clerical)
@mainController.route('/clerical_dashboard')
@login_required
def clerical_dashboard():
    if current_user.employee_position != 'clerical':
        return abort(403)

    waiting_request = db.session.query(Request).filter_by(request_status='waiting').order_by(Request.request_date.desc()).limit(3).all()

    return render_template(
        'clerical/dashboard.html', 
        waiting_request=waiting_request
    )
