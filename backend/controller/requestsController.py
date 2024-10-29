from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from flask_login import login_required, current_user
from models.unit import Unit
# from utils.conversion import convert_to_base_unit, convert_to_largest_unit
from models.product import Product
from models.productList import ProductList
from models.request import Request
from models.requestList import RequestList
from extensions import db
from datetime import datetime
from decimal import Decimal

requestController = Blueprint('request', __name__)

def convert_to_base_unit(quantity, unit, product_type):
    """แปลงหน่วยสินค้าเป็นหน่วยเล็กที่สุด (g สำหรับ Food และ mL สำหรับ Chemical)"""
    if product_type == 'Food':
        if unit == 'kg':
            return quantity * 1000  # แปลง kg เป็น g
        elif unit == 'g':
            return quantity  # ถ้าเป็น g อยู่แล้วไม่ต้องแปลง
        else:
            raise ValueError("Unknown unit for Food")
    
    elif product_type == 'Chemical':
        if unit == 'L':
            return quantity * 1000  # แปลง L เป็น mL
        elif unit == 'mL':
            return quantity  # ถ้าเป็น mL อยู่แล้วไม่ต้องแปลง
        else:
            raise ValueError("Unknown unit for Chemical")
    
    else:
        raise ValueError("Unknown product type")

def convert_to_largest_unit(quantity, product_type):
    """เปลี่ยนหน่วยเป็นหน่วยใหญ่ที่สุด (kg สำหรับ Food และ L สำหรับ Chemical)"""
    if product_type == 'Food':
        if quantity >= 1000:
            return quantity / 1000, 'kg'  # แปลงกลับเป็น kg ถ้าจำนวน >= 1000g
        else:
            return quantity, 'g'  # แสดงเป็น g ถ้าน้อยกว่า 1000g

    elif product_type == 'Chemical':
        if quantity >= 1000:
            return quantity / 1000, 'L'  # แปลงกลับเป็น L ถ้าจำนวน >= 1000mL
        else:
            return quantity, 'mL'  # แสดงเป็น mL ถ้าน้อยกว่า 1000mL

    else:
        raise ValueError("Unknown product type")
    
def convert_to_base_unit1(quantity, unit, product_type):
    """Convert quantities to a base unit."""
    if product_type == 'Food' and unit == 'kg':
        return quantity * 1000  # Convert kg to grams
    elif product_type == 'Chemical' and unit == 'L':
        return quantity * 1000  # Convert liters to milliliters
    return quantity  # No conversion needed for other units

@requestController.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    if current_user.employee.employee_position not in ['worker', 'academic']:
        flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'danger')
        return redirect(url_for('main.index'))
    
    # Get the selected status from the dropdown filter (default to 'all')
    selected_status = request.args.get('status', 'all').lower()

    # Base query to retrieve requests for the current user
    base_query = (
        db.session.query(Request, RequestList, ProductList)
        .join(RequestList, Request.request_id == RequestList.request_id)
        .join(ProductList, RequestList.product_id == ProductList.product_id)
        .filter(Request.employee_id == current_user.employee_id)
        .order_by(Request.request_date.desc())
    )

    # Filter by status if it's not 'all'
    if selected_status != 'all':
        base_query = base_query.filter(Request.request_status.ilike(f'%{selected_status}%'))

    # Get the latest 3 requests
    requests = base_query.limit(3).all()

    request_data = [
        {
            'request_id': req.request_id,
            'product_name': prod.product_name,
            'quantity': req_list.request_quantity,
            'unit': req_list.product_unit,
            'status': req.request_status,
            'date': req.request_date,
        }
        for req, req_list, prod in requests
    ]
    if current_user.employee.employee_position == 'worker':
        return render_template('worker/dashboard.html', requests=request_data, selected_status=selected_status)
    elif current_user.employee.employee_position == 'academic':
        return render_template('academic/dashboard.html', requests=request_data, selected_status=selected_status)

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

    if current_user.employee.employee_position == 'worker':
        return render_template('worker/add_request.html', product_lists=product_lists)
    elif current_user.employee.employee_position == 'academic':
        return render_template('academic/add_request.html', product_lists=product_lists)

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

    # ดึงข้อมูลหน่วยและปริมาณสินค้าจากตาราง Product
    product_stock = Product.query.filter_by(product_id=product_id).first()
    if not product_stock:
        flash('ไม่พบสินค้าคงคลัง', 'danger')
        return redirect(url_for('request.add_request'))

    product_unit = product_stock.product_unit
    total_available_quantity = db.session.query(db.func.sum(Product.product_quantity))\
        .filter(Product.product_id == product_id).scalar()

    if total_available_quantity is None:
        total_available_quantity = 0

    requested_quantity_base = convert_to_base_unit(float(request_quantity), request_unit, product.product_type)
    available_quantity_base = convert_to_base_unit(total_available_quantity, product_unit, product.product_type)

    if requested_quantity_base > available_quantity_base:
        flash('สินค้ามีจำนวนไม่เพียงพอสำหรับการเบิก', 'danger')
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

@requestController.route('/request/product_detail/<product_id>', methods=['GET', 'POST'])
@login_required
def product_detail(product_id):
    if current_user.employee.employee_position not in ['worker', 'academic']:
        flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'danger')
        return redirect(url_for('main.index'))

    # ดึงข้อมูลสินค้าและหน่วยที่เกี่ยวข้อง
    product = ProductList.query.get_or_404(product_id)
    units = Unit.query.filter_by(product_type=product.product_type).all()

    if request.method == 'POST':
        request_quantity = request.form['request_quantity']
        request_unit = request.form['request_unit']

        # เพิ่มสินค้าเข้า cart
        if 'cart' not in session:
            session['cart'] = []
        session['cart'].append({
            'product_id': product_id,
            'product_name': product.product_name,
            'request_quantity': request_quantity,
            'request_unit': request_unit
        })

        flash('เพิ่มสินค้าในรายการสำเร็จ', 'success')
        return redirect(url_for('request.add_request'))
    
    if current_user.employee.employee_position == 'worker':
        return render_template('worker/product_detail.html', product=product, units=units)
    elif current_user.employee.employee_position == 'academic':
        return render_template('academic/product_detail.html', product=product, units=units)

@requestController.route('/request/cart', methods=['GET', 'POST'])
@login_required
def view_cart():
    """แสดง cart และฟังก์ชันสำหรับส่งคำขอเบิก"""
    if current_user.employee.employee_position not in ['worker', 'academic']:
        flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'danger')
        return redirect(url_for('main.index'))

    # ดึงข้อมูลรายการใน cart พร้อมข้อมูลสินค้า (ถ้าจำเป็น)
    cart_items = []
    for item in session.get('cart', []):
        product = ProductList.query.get(item['product_id'])
        if product:
            cart_items.append({
                'product_id': item['product_id'],
                'product_name': product.product_name,
                'product_image': product.product_image,
                'request_quantity': item['request_quantity'],
                'request_unit': item['request_unit']
            })
            
    if current_user.employee.employee_position == 'worker':
        return render_template('worker/cart.html', cart=cart_items)
    elif current_user.employee.employee_position == 'academic':
        return render_template('academic/cart.html', cart=cart_items)

@requestController.route('/request/remove_from_cart/<int:index>', methods=['POST'])
@login_required
def remove_from_cart(index):
    # ลบสินค้าจาก cart
    if 'cart' in session and len(session['cart']) > index:
        session['cart'].pop(index)
        flash('ลบสินค้าออกจากรายการสำเร็จ', 'success')
    return redirect(url_for('request.view_cart'))

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

    return redirect(url_for('request.view_cart'))

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
        request_status='waiting'
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
    return redirect(url_for('request.add_request'))

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

    # กรองตามสถานะคำขอเบิก
    if filter_status == 'accept':
        query = query.filter(Request.request_status == 'accept')
    elif filter_status == 'reject':
        query = query.filter(Request.request_status == 'reject')
    elif filter_status == 'waiting':
        query = query.filter(Request.request_status == 'waiting')

    requests = query.all()

    if current_user.employee.employee_position == 'worker':
        return render_template('worker/history_request.html', requests=requests, search_query=search_query, filter_status=filter_status)
    elif current_user.employee.employee_position == 'academic':
        return render_template('academic/history_request.html', requests=requests, search_query=search_query, filter_status=filter_status)

@requestController.route('/request/confirm', methods=['GET', 'POST'])
@login_required
def confirm_request():
    if current_user.employee.employee_position not in ['clerical', 'keeper']:
    # if current_user.employee.employee_position != 'clerical':
        flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'danger')
        return redirect(url_for('main.index'))

    # รับค่า search และ filter_status จาก query string
    search_query = request.args.get('search', '')
    filter_status = request.args.get('filter_status', 'all')

    # สร้าง query เบื้องต้น
    query = Request.query

    # ถ้ามีค่า search ให้กรองตาม Request ID หรือ Request Date
    if search_query:
        query = query.filter(
            (Request.request_id.ilike(f"%{search_query}%")) |
            (Request.request_date.ilike(f"%{search_query}%"))
        )

    # ถ้า filter_status ไม่ใช่ all ให้กรองตาม request_status
    if filter_status != 'all':
        query = query.filter_by(request_status=filter_status)

    # ดึงข้อมูลตามเงื่อนไข
    requests = query.all()

    if request.method == 'POST':
        request_id = request.form['request_id']
        request_list = RequestList.query.filter_by(request_id=request_id).all()

        for item in request_list:
            # ดึงสินค้าทั้งหมดที่มี product_id เดียวกันจากหลาย lot และทำการ join กับตาราง ProductList เพื่อดึงข้อมูล product_type
            products = db.session.query(Product, ProductList).join(ProductList, Product.product_id == ProductList.product_id).filter(Product.product_id == item.product_id).all()

            if products:
                # แปลง requested_quantity_base เป็นหน่วยฐาน (g หรือ mL)
                requested_quantity_base = convert_to_base_unit(float(item.request_quantity), item.product_unit, products[0].ProductList.product_type)
                remaining_quantity = Decimal(requested_quantity_base)

                for product, product_list in products:
                    # แปลง product_quantity เป็นหน่วยฐานเพื่อลบจำนวนออก
                    product_quantity_base = convert_to_base_unit(float(product.product_quantity), product.product_unit, product_list.product_type)
                    product_quantity_base = Decimal(product_quantity_base)

                    if remaining_quantity <= product_quantity_base:
                        # หักจำนวนสินค้าที่เบิกออกจากสินค้าจาก lot นี้
                        updated_quantity_base = product_quantity_base - remaining_quantity
                        updated_quantity, updated_unit = convert_to_largest_unit(float(updated_quantity_base), product_list.product_type)

                        # อัปเดตจำนวนสินค้าในหน่วยที่ต้องการและ commit
                        product.product_quantity = updated_quantity
                        product.product_unit = updated_unit
                        db.session.commit()
                        break
                    else:
                        # หากสินค้าจาก lot นี้ไม่พอ ให้ใช้จำนวนที่มีทั้งหมด และหัก remaining_quantity ต่อไปใน lot ถัดไป
                        remaining_quantity -= product_quantity_base
                        product.product_quantity = 0
                        db.session.commit()

        # อัปเดตสถานะคำขอเบิกเป็น 'accept'
        req = Request.query.filter_by(request_id=request_id).first()
        req.request_status = 'accept'
        db.session.commit()

        flash('ยืนยันการเบิกสินค้าสำเร็จ', 'success')
        return redirect(url_for('request.confirm_request'))

    if current_user.employee.employee_position == 'clerical':
        return render_template('clerical/confirm_request.html', requests=requests)
    elif current_user.employee.employee_position == 'keeper':
        return render_template('keeper/history_request.html', requests=requests)

@requestController.route('/request/<string:request_id>/details', methods=['GET'])
@login_required
def request_details(request_id):
    if current_user.employee.employee_position not in ['clerical', 'keeper']:
        flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'danger')
        return redirect(url_for('main.index'))
    
    # ดึงรายการสินค้าที่ถูกเบิกตาม request_id
    request = Request.query.filter_by(request_id=request_id).first()
    if not request:
        flash('ไม่พบคำขอเบิกสินค้านี้', 'danger')
        return redirect(url_for('request.confirm_request'))

    # ดึงรายการสินค้าที่เกี่ยวข้องกับคำขอเบิกนี้
    request_list = RequestList.query.filter_by(request_id=request_id).all()

    # return render_template('clerical/request_details.html', request=request, request_list=request_list)
    if current_user.employee.employee_position == 'clerical':
        return render_template('clerical/request_details.html', request=request, request_list=request_list)
    elif current_user.employee.employee_position == 'keeper':
        return render_template('keeper/request_details.html', request=request, request_list=request_list)

@requestController.route('/request/reject', methods=['POST'])
@login_required
def reject_request():
    if current_user.employee.employee_position != 'clerical':
        flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'danger')
        return redirect(url_for('main.index'))

    # เข้าถึง request_id จากข้อมูลฟอร์ม
    request_id = request.form['request_id']

    # ค้นหาคำขอในตาราง Request ที่ตรงกับ request_id
    current_request = Request.query.filter_by(request_id=request_id).first()

    if current_request:
        # อัปเดตสถานะ request_status เป็น 'reject'
        current_request.request_status = 'reject'
        db.session.commit()
        flash(f'คำขอ {request_id} ถูกปฏิเสธเรียบร้อยแล้ว', 'success')
    else:
        flash(f'ไม่พบคำขอ {request_id}', 'danger')

    return redirect(url_for('request.confirm_request'))