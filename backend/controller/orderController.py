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

# Route สำหรับการจัดการคำสั่งซื้อ
@orderController.route('/order')
def manage_order():
    return render_template('order.html')

@orderController.route('/order/add', methods=['GET', 'POST'])
@login_required
def add_order():
    if current_user.employee.employee_position != 'keeper':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))

    # ดึงรายการสินค้าจากตาราง product_lists
    product_lists = ProductList.query.all()

    # ดึงข้อมูลหน่วยจากตาราง units
    units = Unit.query.all()

    # ตรวจสอบว่ามีการเริ่มต้น session สำหรับรายการสั่งซื้อหรือยัง
    if 'cart' not in session:
        session['cart'] = []

    # กรณีเพิ่มสินค้าในรายการสั่งซื้อ
    if request.method == 'POST' and 'add_to_cart' in request.form:
        product_id = request.form['product_id']
        product_quantity = request.form['product_quantity']
        
        # แทนที่การใช้ ID ด้วยการดึงชื่อหน่วยจากฐานข้อมูล
        unit_id = request.form['product_unit']
        product_unit = Unit.query.filter_by(unit_id=unit_id).first().unit_name  # ดึงชื่อของหน่วยมาแทน

        # ดึงข้อมูลชื่อสินค้า
        product = ProductList.query.filter_by(product_id=product_id).first()
        product_name = product.product_name if product else 'Unknown'

        # เพิ่มสินค้าใน cart โดยเพิ่มชื่อสินค้าเข้าไปด้วย
        session['cart'].append({
            'product_id': product_id,
            'product_name': product_name,  # เพิ่มชื่อสินค้าเข้าไปใน session
            'product_quantity': product_quantity,
            'product_unit': product_unit  # บันทึกชื่อของหน่วยแทน
        })
        flash('Product added to cart!', 'success')
        return redirect(url_for('order.add_order'))
    
    # ดึงข้อมูลชื่อสินค้าใน cart จาก product_lists
    cart_with_names = []
    for item in session['cart']:
        product = ProductList.query.filter_by(product_id=item['product_id']).first()
        cart_with_names.append({
            'product_id': item['product_id'],
            'product_name': item['product_name'],  # แสดงชื่อของสินค้า
            'product_quantity': item['product_quantity'],
            'product_unit': item['product_unit']  # แสดงชื่อของหน่วย
        })

    # กรณีบันทึกคำสั่งซื้อทั้งหมด
    if request.method == 'POST' and 'submit_order' in request.form:
        order_id = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        order_date = datetime.now()
        employee_id = current_user.employee.employee_id
        order_status = False

        # เพิ่มคำสั่งซื้อในตาราง orders
        new_order = Order(order_id=order_id, order_date=order_date, employee_id=employee_id, order_status=order_status)
        db.session.add(new_order)

        lot_id = f"LOT-{datetime.now().strftime('%Y%m%d%H%M%S')}"  # สร้าง lot_id แบบไม่ซ้ำ
        lot_date = datetime.now()

        # เพิ่มข้อมูลในตาราง product_lots
        new_lot = ProductLot(lot_id=lot_id, lot_date=lot_date)
        db.session.add(new_lot)

        # บันทึกรายการสินค้าที่อยู่ใน session
        for item in session['cart']:
            product_id = item['product_id']
            product_quantity = item['product_quantity']
            product_unit = item['product_unit']  # บันทึกชื่อหน่วย

            # เพิ่มรายละเอียดคำสั่งซื้อในตาราง order_lists
            new_order_list = OrderList(
                order_id=order_id,
                product_id=product_id,
                product_quantity=product_quantity,
                product_unit=product_unit,  # บันทึกชื่อของหน่วย
                lot_id=lot_id
            )
            db.session.add(new_order_list)

        # เคลียร์ cart หลังจากบันทึกเสร็จ
        session.pop('cart', None)
        db.session.commit()
        flash('Order placed successfully!', 'success')
        return redirect(url_for('order.order_history'))

    return render_template('keeper/add_order.html', product_lists=product_lists, units=units, cart=session['cart'])

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
        session['cart'][index]['product_quantity'] = new_quantity  # แก้ไขจำนวนสินค้า
        flash('Item quantity updated!', 'success')
    return redirect(url_for('order.add_order'))

# Route สำหรับแสดงประวัติการซื้อ
@orderController.route('/order/history', methods=['GET'])
@login_required
def order_history():
    if current_user.employee.employee_position != 'keeper':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))

    orders = Order.query.filter_by(employee_id = current_user.employee.employee_id).all()
    return render_template('keeper/order_history.html', orders=orders)
