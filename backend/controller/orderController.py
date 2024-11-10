from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from models.product import Product
from models.productList import ProductList
from models.productLot import ProductLot
from models.order import Order
from models.orderList import OrderList
from models.unit import Unit
from extensions import db
from datetime import datetime
from utils.conversion import convert_to_base_unit, convert_to_largest_unit

orderController = Blueprint('order', __name__)

@orderController.route('/order/add', methods=['GET'])
@login_required
def add_order():
    if current_user.employee_position != 'keeper':
        # flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))

    # แปลง quantity ให้เป็นหน่วยเล็กก่อนเปรียบเทียบกับ threshold
    products = Product.query.filter((Product.product_quantity * 1000) <= Product.threshold).all()
    return render_template('keeper/add_order.html', product_lists=products)

@orderController.route('/order/product_detail/<product_id>', methods=['GET', 'POST'])
@login_required
def product_detail(product_id):
    if current_user.employee_position != 'keeper':
        # flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))

    # ดึงข้อมูลสินค้าและหน่วยที่เกี่ยวข้อง
    product = Product.query.get_or_404(product_id)
    units = Unit.query.all()

    if request.method == 'POST':
        order_quantity = request.form['order_quantity']
        unit_id = request.form['product_unit']
        product_unit = Unit.query.filter_by(unit_id=unit_id).first().unit_id

        # เพิ่มสินค้าลงใน session cart
        if 'cart' not in session:
            session['cart'] = []
            session['cart'].append({
            'product_id': product_id,
            'product_name': product.product_name,
            'order_quantity': order_quantity,
            'product_image': product.product_image,
            'product_unit': unit_id
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
    # product_image = request.form['product_image']
    unit_id = request.form['product_unit']
    product_unit = Unit.query.filter_by(unit_id=unit_id).first().unit_name  # ดึงชื่อของหน่วยมาแทน

    # ดึง product_image จาก ProductList
    product = Product.query.filter_by(product_id=product_id).first()
    product_image = product.product_image if product else None

    # ตรวจสอบว่ามี session cart แล้วหรือยัง
    if 'cart' not in session:
        session['cart'] = []

    # เพิ่มสินค้าเข้า cart
    session['cart'].append({
        'product_id': product_id,
        'order_quantity': order_quantity,
        'product_image': product_image,
        'product_unit': unit_id
    })
    flash('Product added to cart!', 'success')
    return redirect(url_for('order.add_order'))

@orderController.route('/order/cart', methods=['GET', 'POST'])
@login_required
def view_cart():
    """ฟังก์ชันแสดง cart และยืนยันคำสั่งซื้อ"""
    if current_user.employee_position != 'keeper':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))

    # Query Product เพื่อดึง product_name ตาม product_id
    for item in session.get('cart', []):
        product = Product.query.filter_by(product_id=item['product_id']).first()
        if product:
            item['product_name'] = product.product_name  # เพิ่ม `product_name` ใน cart item

    # ส่วนที่เหลือของฟังก์ชัน view_cart
    if request.method == 'POST' and 'submit_order' in request.form:
        if 'cart' not in session or len(session['cart']) == 0:
            flash('ไม่สามารถส่งคำสั่งซื้อได้ เนื่องจากไม่มีสินค้าในรายการ', 'danger')
            return redirect(url_for('order.view_cart'))

        # ดำเนินการบันทึกคำสั่งซื้อ
        order_id = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        order_date = datetime.now()
        employee_id = current_user.employee.employee_id
        order_status = 'waiting'

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

@orderController.route('/order/submit_order', methods=['POST'])
@login_required
def submit_order():
    """บันทึกคำสั่งซื้อจากข้อมูลใน cart"""
    if 'cart' not in session or len(session['cart']) == 0:
        flash('ไม่สามารถส่งคำสั่งซื้อได้ เนื่องจากไม่มีสินค้าในรายการ', 'danger')
        return redirect(url_for('order.view_cart'))

    # เริ่มบันทึกคำสั่งซื้อ
    order_id = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    order_date = datetime.now()
    employee_id = current_user.employee_id
    order_status = 'waiting'

    # สร้างรายการคำสั่งซื้อใหม่ในตาราง orders
    new_order = Order(order_id=order_id, employee_id=employee_id, order_date=order_date, order_status=order_status)
    db.session.add(new_order)

    # counter_lot = 1
    # for item in session['cart']:
    #     new_lot = ProductLot(
    #         lot_id = f"LOT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{counter_lot}",
    #         product_id = item['product_id'],
    #         lot_quantity = item['order_quantity']
    #     )
    #     db.session.add(new_lot)
    #     counter_lot += 1

    counter_order = 1
    for item in session['cart']:
        new_order_list = OrderList(
            order_list_id = f"ORDL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{counter_order}",
            order_id = order_id,
            product_id = item['product_id'],
            unit_id = item['product_unit'],
            order_quantity = item['order_quantity']
        )
        db.session.add(new_order_list)
        counter_order += 1

    # เคลียร์ cart หลังจากบันทึกเสร็จ
    session.pop('cart', None)
    db.session.commit()
    flash('Order placed successfully!', 'success')
    return redirect(url_for('order.order_history'))

@orderController.route('/order/cart/remove/<int:index>', methods=['POST'])
@login_required
def remove_cart_item(index):
    if 'cart' in session and index < len(session['cart']):
        session['cart'].pop(index)
        flash('Item removed from cart!', 'success')
    return redirect(url_for('order.view_cart'))

@orderController.route('/order/cart/edit/<int:index>', methods=['POST'])
@login_required
def edit_cart_item(index):
    new_quantity = request.form['new_quantity']
    
    # ตรวจสอบว่ามี cart และ index ที่ถูกต้องหรือไม่
    if 'cart' in session and index < len(session['cart']):
        session['cart'][index]['order_quantity'] = new_quantity  # แก้ไขจำนวนสินค้า
        flash('Item quantity updated!', 'success')
    return redirect(url_for('order.view_cart'))

@orderController.route('/order/<order_id>/update_status', methods=['POST'])
@login_required
def update_order_status(order_id):
    if current_user.employee_position != 'clerical':
        # flash('You do not have permission to access this page.', 'danger')
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

    # หากสถานะเป็น 'accept' ให้สร้าง product_lot ขึ้นมาตามจำนวนใน order_lists และอัปเดตจำนวนสินค้าคงคลัง
    if new_status == 'accept':
        order_items = OrderList.query.filter_by(order_id=order_id).all()  # สมมติว่า OrderList คือโมเดลสำหรับรายการสินค้าใน order
        counter_lot = 1
        for item in order_items:
            # ดึงสินค้าจากตาราง products
            product = Product.query.filter_by(product_id=item.product_id).first()
            if not product:
                flash(f'Product with ID {item.product_id} not found.', 'danger')
                continue

            # ดึง unit_name จากตาราง unit ตาม unit_id ใน OrderList
            unit = Unit.query.filter_by(unit_id=item.unit_id).first()
            if not unit:
                flash(f'Unit with ID {item.unit_id} not found.', 'danger')
                continue

            # ตรวจสอบว่าเป็นหน่วยใหญ่หรือเล็กและแปลงหน่วยตามความเหมาะสม
            if unit.unit_name in ['Kg', 'L']:
                # ถ้าเป็นหน่วยใหญ่ เพิ่มจำนวนสินค้าได้เลย
                product.product_quantity += item.order_quantity
            elif unit.unit_name in ['g', 'mL']:
                # ถ้าเป็นหน่วยเล็ก แปลงเป็นหน่วยใหญ่ก่อนแล้วจึงเพิ่มจำนวนสินค้า
                base_quantity = convert_to_base_unit(item.order_quantity, unit.unit_name, product.product_type)
                final_quantity, _ = convert_to_largest_unit(base_quantity, product.product_type)
                product.product_quantity += final_quantity
            else:
                flash(f'Unknown unit for {product.product_type} with unit {unit.unit_name}', 'danger')
                continue

            # สร้าง lot ใหม่สำหรับสินค้า
            new_product_lot = ProductLot(
                lot_id=f"LOT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{counter_lot}",
                product_id=item.product_id,
                lot_date = datetime.now(),
                lot_quantity=item.order_quantity
            )
            db.session.add(new_product_lot)
            counter_lot += 1

        db.session.commit()
        flash(f'Product lots created for Order {order_id} and inventory updated!', 'success')

    # กลับไปหน้า order_history พร้อมกับตัวกรองและการค้นหาเดิม
    return redirect(url_for('order.order_history', search=request.args.get('search'), filter_status=request.args.get('filter_status')))

@orderController.route('/order/history', methods=['GET'])
@login_required
def order_history():
    if current_user.employee_position not in ['keeper', 'clerical']:
        # flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))

    # ดึงข้อมูลการค้นหาและตัวกรองจาก query parameters
    search_query = request.args.get('search', '')
    filter_status = request.args.get('filter_status', '')

    # ถ้า filter_status เป็นค่าว่าง กำหนด orders ให้เป็นลิสต์ว่าง
    if not filter_status:
        orders = []  # ไม่มีข้อมูลแสดง
    else:
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
    if filter_status:
        if filter_status == 'accept':
            query = query.filter_by(order_status='accept')
        elif filter_status == 'reject':
            query = query.filter_by(order_status='reject')
        elif filter_status == 'waiting':
            query = query.filter_by(order_status='waiting')
        elif filter_status == 'done':
            query = query.filter_by(order_status='done')

        # ดึงข้อมูลคำสั่งซื้อที่ค้นหาและกรองแล้ว
        orders = query.order_by(Order.order_date.desc()).all()

    if current_user.employee_position == 'keeper':
        return render_template('keeper/order_history.html', orders=orders)
    elif current_user.employee_position == 'clerical':
        return render_template('clerical/confirm_order.html', orders=orders)

@orderController.route('/order/<order_id>', methods=['GET'])
@login_required
def view_order_details(order_id):
    if current_user.employee_position not in ['keeper', 'clerical']:
        # flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))

    # ดึงรายละเอียดคำสั่งซื้อจากตาราง order_lists
    order = Order.query.filter_by(order_id=order_id).first_or_404()

    # ดึง order_items ที่มี product_id ตรงกับตาราง products
    order_items = (
    db.session.query(
        OrderList.order_id,
        OrderList.order_quantity,
        OrderList.product_id,
        Product.product_name,
        Product.product_image,
        Unit.unit_name
    )
    .join(Product, OrderList.product_id == Product.product_id)
    .join(Unit, OrderList.unit_id == Unit.unit_id)
    .filter(OrderList.order_id == order_id)
    .all()
)

    if current_user.employee_position == 'keeper':
        return render_template('keeper/order_details.html', order=order, order_items=order_items)
    elif current_user.employee_position == 'clerical':
        return render_template('clerical/order_details.html', order=order, order_items=order_items)
    
@orderController.route('/order/cart/cancel', methods=['POST'])
@login_required
def cancel_cart():
    session.pop('cart', None)
    flash('Cart cleared!', 'success')
    return redirect(url_for('order.view_cart'))
