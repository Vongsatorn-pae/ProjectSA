from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from flask_login import login_required, current_user
from models.product import Product
from models.productList import ProductList
from models.request import Request
from models.requestList import RequestList
from extensions import db
from datetime import datetime

requestController = Blueprint('request', __name__)

@requestController.route('/request/add', methods=['GET', 'POST'])
@login_required
def add_request():
    if current_user.employee.employee_position not in ['worker', 'academic']:
        flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'danger')
        return redirect(url_for('main.index'))

    product_lists = ProductList.query.all()

    # ตรวจสอบว่ามีการเริ่มต้น session สำหรับ cart หรือยัง
    if 'cart' not in session:
        session['cart'] = []

    return render_template('worker/add_request.html', product_lists=product_lists)

@requestController.route('/request/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    product_id = request.form['product_id']
    request_quantity = request.form['request_quantity']
    request_unit = request.form['request_unit']

    # ตรวจสอบสินค้าจากฐานข้อมูล
    product = ProductList.query.filter_by(product_id=product_id).first()
    if not product:
        flash('ไม่พบสินค้าที่เลือก', 'danger')
        return redirect(url_for('request.add_request'))

    # เพิ่มสินค้าเข้า cart
    session['cart'].append({
        'product_id': product_id,
        'product_name': product.product_name,
        'request_quantity': request_quantity,
        'request_unit': request_unit
    })
    flash('เพิ่มสินค้าในรายการสำเร็จ', 'success')
    return redirect(url_for('request.add_request'))

@requestController.route('/request/remove_from_cart/<int:index>', methods=['POST'])
@login_required
def remove_from_cart(index):
    # ลบสินค้าจาก cart
    if 'cart' in session and len(session['cart']) > index:
        session['cart'].pop(index)
        flash('ลบสินค้าออกจากรายการสำเร็จ', 'success')
    return redirect(url_for('request.add_request'))

@requestController.route('/request/update_cart_item/<int:index>', methods=['POST'])
@login_required
def update_cart_item(index):
    new_quantity = request.form['new_quantity']

    # ตรวจสอบว่า cart มีสินค้าอยู่ในตำแหน่งที่ถูกต้อง
    if 'cart' in session and len(session['cart']) > index:
        session['cart'][index]['request_quantity'] = new_quantity
        flash('อัปเดตจำนวนสินค้าสำเร็จ', 'success')
    else:
        flash('ไม่พบสินค้าที่ต้องการแก้ไข', 'danger')

    return redirect(url_for('request.add_request'))

@requestController.route('/request/submit_request', methods=['POST'])
@login_required
def submit_request():
    if 'cart' not in session or len(session['cart']) == 0:
        flash('ไม่สามารถส่งคำขอเบิกได้เนื่องจากไม่มีสินค้าในรายการ', 'danger')
        return redirect(url_for('request.add_request'))

    # สร้าง request_id ใหม่
    request_id = f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    employee_id = current_user.employee.employee_id
    request_date = datetime.now()

    # เพิ่มข้อมูลในตาราง requests
    new_request = Request(
        request_id=request_id,
        request_date=request_date,
        employee_id=employee_id,
        request_status=False
    )
    db.session.add(new_request)
    db.session.commit()

    # เพิ่มข้อมูลสินค้าใน cart เข้าใน request_lists
    for item in session['cart']:
        new_request_list = RequestList(
            request_id=request_id,
            product_id=item['product_id'],
            request_quantity=item['request_quantity'],
            product_unit=item['request_unit']
        )
        db.session.add(new_request_list)

    # ล้าง cart หลังจากบันทึกเสร็จ
    session.pop('cart', None)
    db.session.commit()
    flash('ส่งคำขอเบิกสินค้าสำเร็จ', 'success')
    return redirect(url_for('request.view_history'))

# หน้าประวัติการขอเบิกสินค้า
@requestController.route('/request/history', methods=['GET'])
@login_required
def view_history():
    search_query = request.args.get('search', '')  # ดึงค่าจาก search bar
    filter_status = request.args.get('status', 'all')  # ดึงค่าจากตัวกรองสถานะ
    
    # Query พื้นฐานสำหรับดึงข้อมูล request ทั้งหมด
    query = db.session.query(Request, RequestList, ProductList).join(RequestList, Request.request_id == RequestList.request_id)\
        .join(ProductList, RequestList.product_id == ProductList.product_id)\
        .filter(Request.employee_id == current_user.employee.employee_id)

    # ถ้ามีการค้นหา ให้กรองข้อมูลตามชื่อสินค้า
    if search_query:
        query = query.filter(ProductList.product_name.ilike(f'%{search_query}%'))

    # ถ้าตัวกรองสถานะถูกเลือก ให้กรองตามสถานะการยืนยัน
    if filter_status == 'approved':
        query = query.filter(Request.request_status == True)
    elif filter_status == 'pending':
        query = query.filter(Request.request_status == False)

    requests = query.all()

    return render_template('worker/history_request.html', requests=requests, search_query=search_query, filter_status=filter_status)

@requestController.route('/request/approve', methods=['GET', 'POST'])
@login_required
def approve_request():
    if current_user.employee.employee_position != 'clerical':
        flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'danger')
        return redirect(url_for('main.index'))

    requests = Request.query.filter_by(status=False).all()

    if request.method == 'POST':
        request_id = request.form['request_id']
        request_list = RequestList.query.filter_by(request_id=request_id).all()

        for item in request_list:
            product = Product.query.filter_by(product_id=item.product_id).first()
            product.product_quantity -= item.request_quantity  # ลดจำนวนสินค้าในสต็อก
            db.session.commit()

        # อัพเดตสถานะของคำขอเบิก
        req = Request.query.filter_by(request_id=request_id).first()
        req.status = True
        db.session.commit()

        flash('ยืนยันการเบิกสินค้าสำเร็จ', 'success')
        return redirect(url_for('request.approve_request'))

    return render_template('request/approve_request.html', requests=requests)
