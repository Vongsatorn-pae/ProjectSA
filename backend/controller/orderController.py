from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from models.productList import ProductList
from models.productLot import ProductLot
from models.order import Order
from models.orderList import OrderList
from models.unit import Unit
from extensions import db
from datetime import datetime

orderController = Blueprint('order', __name__)

@orderController.route('/order/add', methods=['GET'])
@login_required
def add_order():
    if current_user.employee.employee_position != 'keeper':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))

    # ดึงรายการสินค้าทั้งหมด
    product_lists = ProductList.query.all()
    return render_template('keeper/add_order.html', product_lists=product_lists)

@orderController.route('/order/product_detail/<product_id>', methods=['GET', 'POST'])
@login_required
def product_detail(product_id):
    if current_user.employee.employee_position != 'keeper':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))

    # ดึงข้อมูลสินค้าและหน่วยที่เกี่ยวข้อง
    product = ProductList.query.get_or_404(product_id)
    units = Unit.query.all()

    if request.method == 'POST':
        order_quantity = request.form['order_quantity']
        unit_id = request.form['product_unit']
        product_unit = Unit.query.filter_by(unit_id=unit_id).first().unit_name

        # เพิ่มสินค้าลงใน session cart
        if 'cart' not in session:
            session['cart'] = []
        session['cart'].append({
            'product_id': product_id,
            'product_name': product.product_name,
            'order_quantity': order_quantity,
            'product_unit': product_unit
        })

        flash('Product added to cart!', 'success')
        return redirect(url_for('order.view_cart'))

    return render_template('keeper/product_detail.html', product=product, units=units)

@orderController.route('/order/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    """ฟังก์ชันสำหรับเพิ่มสินค้าเข้า cart และเปลี่ยนไปหน้า cart"""
    product_id = request.form['product_id']
    order_quantity = request.form['order_quantity']
    unit_id = request.form['product_unit']
    product_unit = Unit.query.filter_by(unit_id=unit_id).first().unit_name  # ดึงชื่อของหน่วยมาแทน

    # ตรวจสอบว่ามี session cart แล้วหรือยัง
    if 'cart' not in session:
        session['cart'] = []

    # เพิ่มสินค้าเข้า cart
    session['cart'].append({
        'product_id': product_id,
        'order_quantity': order_quantity,
        'product_unit': product_unit
    })
    flash('Product added to cart!', 'success')
    return redirect(url_for('order.add_order'))


@orderController.route('/order/cart', methods=['GET', 'POST'])
@login_required
def view_cart():
    """ฟังก์ชันแสดง cart และยืนยันคำสั่งซื้อ"""
    if current_user.employee.employee_position != 'keeper':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST' and 'submit_order' in request.form:
        if 'cart' not in session or len(session['cart']) == 0:
            flash('ไม่สามารถส่งคำสั่งซื้อได้ เนื่องจากไม่มีสินค้าในรายการ', 'danger')
            return redirect(url_for('order.view_cart'))

        # ดำเนินการบันทึกคำสั่งซื้อ
        order_id = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        order_date = datetime.now()
        employee_id = current_user.employee.employee_id
        order_status = 'waiting'

        # บันทึกคำสั่งซื้อในตาราง orders
        new_order = Order(order_id=order_id, order_date=order_date, employee_id=employee_id, order_status=order_status)
        db.session.add(new_order)

        lot_id = f"LOT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        lot_date = datetime.now()
        new_lot = ProductLot(lot_id=lot_id, lot_date=lot_date)
        db.session.add(new_lot)

        for item in session['cart']:
            product_id = item['product_id']
            order_quantity = item['order_quantity']
            product_unit = item['product_unit']

            new_order_list = OrderList(
                order_id=order_id,
                product_id=product_id,
                order_quantity=order_quantity,
                product_unit=product_unit,
                lot_id=lot_id
            )
            db.session.add(new_order_list)

        # เคลียร์ cart หลังจากบันทึกเสร็จ
        session.pop('cart', None)
        db.session.commit()
        flash('Order placed successfully!', 'success')
        return redirect(url_for('order.order_history'))

    return render_template('keeper/cart.html', cart=session.get('cart', []))

@orderController.route('/order/cart/remove/<int:index>', methods=['POST'])
@login_required
def remove_cart_item(index):
    """Route สำหรับลบรายการใน cart ตาม index ที่กำหนด"""
    if 'cart' in session and index < len(session['cart']):
        session['cart'].pop(index)  # ลบรายการที่ index นั้น
        flash('Item removed from cart!', 'success')
    return redirect(url_for('order.add_order'))

@orderController.route('/order/cart/edit/<int:index>', methods=['POST'])
@login_required
def edit_cart_item(index):
    """Route สำหรับแก้ไขจำนวนสินค้าใน cart"""
    new_quantity = request.form['new_quantity']
    
    # ตรวจสอบว่ามี cart และ index ที่ถูกต้องหรือไม่
    if 'cart' in session and index < len(session['cart']):
        session['cart'][index]['order_quantity'] = new_quantity  # แก้ไขจำนวนสินค้า
        flash('Item quantity updated!', 'success')
    return redirect(url_for('order.add_order'))

@orderController.route('/order/<order_id>/update_status', methods=['POST'])
@login_required
def update_order_status(order_id):
    """Route สำหรับเปลี่ยนสถานะคำสั่งซื้อ"""
    if current_user.employee.employee_position != 'keeper':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))

    # ดึงคำสั่งซื้อตาม order_id
    order = Order.query.filter_by(order_id=order_id).first_or_404()

    # อ่านค่าสถานะใหม่จากฟอร์ม
    new_status = request.form.get('new_status')
    
    if new_status not in ['accept', 'reject', 'waiting']:
        flash('Invalid status update.', 'danger')
        return redirect(url_for('order.order_history'))

    # อัปเดตสถานะคำสั่งซื้อ
    order.order_status = new_status
    db.session.commit()
    flash(f'Order {order_id} status updated to {new_status.capitalize()}!', 'success')

    # กลับไปหน้า order_history พร้อมกับตัวกรองและการค้นหาเดิม
    return redirect(url_for('order.order_history', search=request.args.get('search'), filter_status=request.args.get('filter_status')))

@orderController.route('/order/history', methods=['GET'])
@login_required
def order_history():
    if current_user.employee.employee_position != 'keeper':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))

    # ดึงข้อมูลการค้นหาและตัวกรองจาก query parameters
    search_query = request.args.get('search', '')
    filter_status = request.args.get('filter_status', 'all')

    # เริ่มต้น query สำหรับคำสั่งซื้อ
    query = Order.query

    # ถ้ามีการค้นหา ให้ทำการค้นหาจาก order_id หรือ order_date
    if search_query:
        query = query.filter(
            db.or_(
                Order.order_id.like(f'%{search_query}%'),
                Order.order_date.like(f'%{search_query}%')
            )
        )

    # กรองตามสถานะคำสั่งซื้อ
    if filter_status == 'accept':
        query = query.filter_by(order_status='accept')
    elif filter_status == 'reject':
        query = query.filter_by(order_status='reject')
    elif filter_status == 'waiting':
        query = query.filter_by(order_status='waiting')

    # ดึงข้อมูลคำสั่งซื้อที่ค้นหาและกรองแล้ว
    orders = query.all()

    return render_template('keeper/order_history.html', orders=orders)

@orderController.route('/order/<order_id>', methods=['GET'])
@login_required
def view_order_details(order_id):
    """Route สำหรับแสดงรายละเอียดคำสั่งซื้อ"""
    if current_user.employee.employee_position != 'keeper':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))

    # ดึงรายละเอียดคำสั่งซื้อจากตาราง order_lists
    order = Order.query.filter_by(order_id=order_id).first_or_404()
    order_items = OrderList.query.filter_by(order_id=order_id).all()

    return render_template('keeper/order_details.html', order=order, order_items=order_items)
