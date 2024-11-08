from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from flask_login import login_required, current_user
from models.unit import Unit
# from utils.conversion import convert_to_base_unit, convert_to_largest_unit
from models.product import Product
from models.productLot import ProductLot
# from models.productList import ProductList
from models.request import Request
from models.requestList import RequestList
from extensions import db
from datetime import datetime
from decimal import Decimal

requestController = Blueprint('request', __name__)

def convert_to_base_unit(quantity, unit, product_type):
    """แปลงหน่วยสินค้าเป็นหน่วยเล็กที่สุด (g สำหรับ Food และ mL สำหรับ Chemical)"""
    if product_type == 'Food':
        if unit == 'Kg':
            return quantity * 1000  # แปลง Kg เป็น g
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
    """เปลี่ยนหน่วยเป็นหน่วยใหญ่ที่สุด (Kg สำหรับ Food และ L สำหรับ Chemical)"""
    if product_type == 'Food':
        if quantity >= 1000:
            return quantity / 1000, 'Kg'  # แปลงกลับเป็น Kg ถ้าจำนวน >= 1000g
        else:
            return quantity, 'g'  # แสดงเป็น g ถ้าน้อยกว่า 1000g

    elif product_type == 'Chemical':
        if quantity >= 1000:
            return quantity / 1000, 'L'  # แปลงกลับเป็น L ถ้าจำนวน >= 1000mL
        else:
            return quantity, 'mL'  # แสดงเป็น mL ถ้าน้อยกว่า 1000mL

    else:
        raise ValueError("Unknown product type")

@requestController.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    if current_user.employee_position not in ['worker', 'academic']:
        flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'danger')
        return redirect(url_for('main.index'))
    
    selected_status = request.args.get('status', 'all').lower()

    base_query = db.session.query(Request).filter(Request.employee_id == current_user.employee_id).order_by(Request.request_date.desc())

    if selected_status != 'all':
        base_query = base_query.filter(Request.request_status.ilike(f'%{selected_status}%'))

    requests = base_query.limit(3).all()

    if current_user.employee_position == 'worker':
        return render_template('worker/dashboard.html', requests=requests, selected_status=selected_status)
    elif current_user.employee_position == 'academic':
        return render_template('academic/dashboard.html', requests=requests, selected_status=selected_status)

@requestController.route('/request/add', methods=['GET', 'POST'])
@login_required
def add_request():
    if current_user.employee_position not in ['worker', 'academic']:
        flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'danger')
        return redirect(url_for('main.index'))

    products = Product.query.all()

    if 'cart' not in session:
        session['cart'] = []

    if current_user.employee_position == 'worker':
        return render_template('worker/add_request.html', products=products)
    elif current_user.employee_position == 'academic':
        return render_template('academic/add_request.html', products=products)

@requestController.route('/request/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    product_id = request.form['product_id']
    request_quantity = request.form['request_quantity']
    request_unit = request.form['request_unit']

    # product = ProductList.query.filter_by(product_id=product_id).first()
    product = Product.query.filter_by(product_id=product_id).first()
    if not product:
        flash('ไม่พบสินค้าที่เลือก', 'danger')
        return redirect(url_for('request.add_request'))

    # # ดึงข้อมูลหน่วยและปริมาณสินค้าจากตาราง Product
    # product_stock = Product.query.filter_by(product_id=product_id).first()
    # if not product_stock:
    #     flash('ไม่พบสินค้าคงคลัง', 'danger')
    #     return redirect(url_for('request.add_request'))

    product_unit = product.product_unit
    total_available_quantity = db.session.query(db.func.sum(Product.product_quantity)).filter(Product.product_id == product_id).scalar()

    if total_available_quantity is None:
        total_available_quantity = 0

    unit = db.session.query(Unit).filter(Unit.unit_id == request_unit).first()

    requested_quantity_base = convert_to_base_unit(float(request_quantity), unit.unit_name, product.product_type)
    available_quantity_base = convert_to_base_unit(total_available_quantity, product_unit, product.product_type)

    if requested_quantity_base > available_quantity_base:
        flash('สินค้ามีจำนวนไม่เพียงพอสำหรับการเบิก', 'danger')
        return redirect(url_for('request.add_request'))

    # เพิ่มสินค้าเข้า cart
    session['cart'].append({
        'product_id': product_id,
        'product_name': product.product_name,
        'request_quantity': request_quantity,
        'product_image': product.product_image,
        'request_unit': unit.unit_id
    })
    
    flash('เพิ่มสินค้าในรายการสำเร็จ', 'success')
    return redirect(url_for('request.add_request'))

@requestController.route('/request/product_detail/<product_id>', methods=['GET', 'POST'])
@login_required
def product_detail(product_id):
    if current_user.employee_position not in ['worker', 'academic']:
        flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'danger')
        return redirect(url_for('main.index'))

    # product = ProductList.query.get_or_404(product_id)
    # units = Unit.query.filter_by(product_type=product.product_type).all()
    product = Product.query.get_or_404(product_id)
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
    
    if current_user.employee_position == 'worker':
        return render_template('worker/product_detail.html', product=product, units=units)
    elif current_user.employee_position == 'academic':
        return render_template('academic/product_detail.html', product=product, units=units)

@requestController.route('/request/cart', methods=['GET', 'POST'])
@login_required
def view_cart():
    """แสดง cart และฟังก์ชันสำหรับส่งคำขอเบิก"""
    if current_user.employee_position not in ['worker', 'academic']:
        flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'danger')
        return redirect(url_for('main.index'))

    # cart_items = []
    # for item in session.get('cart', []):
    #     product = ProductList.query.get(item['product_id'])
    #     if product:
    #         cart_items.append({
    #             'product_id': item['product_id'],
    #             'product_name': product.product_name,
    #             'product_image': product.product_image,
    #             'request_quantity': item['request_quantity'],
    #             'request_unit': item['request_unit']
    #         })
    cart_items = []
    for item in session.get('cart', []):
        product = Product.query.get(item['product_id'])
        if product:
            cart_items.append({
                'product_id': item['product_id'],
                'product_name': product.product_name,
                'product_image': product.product_image,
                'request_quantity': item['request_quantity'],
                'request_unit': item['request_unit']
            })
            
    if current_user.employee_position == 'worker':
        return render_template('worker/cart.html', cart=cart_items)
    elif current_user.employee_position == 'academic':
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
    employee_id = current_user.employee_id
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
    counter_request = 1
    for item in session['cart']:
        new_request_list = RequestList(
            # request_list_id = f"REQL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            request_list_id = f"REQL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{counter_request}",
            request_id = request_id,
            product_id = item['product_id'],
            unit_id = item['request_unit'],
            request_quantity = item['request_quantity']
        )
        db.session.add(new_request_list)
        counter_request += 1

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
    # query = db.session.query(Request, RequestList, ProductList).join(RequestList, Request.request_id == RequestList.request_id)\
    #     .join(ProductList, RequestList.product_id == ProductList.product_id)\
    #     .filter(Request.employee_id == current_user.employee_id)
    query = db.session.query(Request).filter(Request.employee_id == current_user.employee_id)

    # ถ้ามีการค้นหา ให้กรองข้อมูลตามชื่อสินค้า
    if search_query:
        query = query.filter(Request.request_id.ilike(f'%{search_query}%'))

    # กรองตามสถานะคำขอเบิก
    if filter_status == 'accept':
        query = query.filter(Request.request_status == 'accept')
    elif filter_status == 'reject':
        query = query.filter(Request.request_status == 'reject')
    elif filter_status == 'waiting':
        query = query.filter(Request.request_status == 'waiting')

    requests = query.all()

    if current_user.employee_position == 'worker':
        return render_template('worker/history_request.html', requests=requests, search_query=search_query, filter_status=filter_status)
    elif current_user.employee_position == 'academic':
        return render_template('academic/history_request.html', requests=requests, search_query=search_query, filter_status=filter_status)

@requestController.route('/request/confirm', methods=['GET', 'POST'])
@login_required
def confirm_request():
    if current_user.employee_position not in ['clerical', 'keeper']:
        flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'danger')
        return redirect(url_for('main.index'))

    # รับค่า search และ filter_status จาก query string
    search_query = request.args.get('search', '')
    filter_status = request.args.get('filter_status', 'all')
    filter_type = request.args.get('filter_type', 'all')

    # ตรวจสอบตำแหน่งของ employee เพื่อกำหนด filter_type อัตโนมัติ
    if filter_type == 'all':  
        if current_user.employee_position == 'worker':
            filter_type = 'Food'
        elif current_user.employee_position == 'academic':
            filter_type = 'Chemical'

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

    # กรองตาม filter_type ที่กำหนดจากตำแหน่ง employee โดย join กับ products ผ่าน request_lists
    if filter_type != 'all':
        query = query.join(RequestList, Request.request_id == RequestList.request_id)\
                    .join(Product, RequestList.product_id == Product.product_id)\
                    .filter(Product.product_type == filter_type)

    # ดึงข้อมูลตามเงื่อนไข
    requests = query.all()

    if request.method == 'POST':
        request_id = request.form['request_id']
        # Join กับตาราง units เพื่อดึง unit_name
        request_list = db.session.query(RequestList, Unit.unit_name).join(Unit, RequestList.unit_id == Unit.unit_id).filter(RequestList.request_id == request_id).all()

        for item, unit_name in request_list:
            # ดึงสินค้าจากหลาย lot และ join กับ products เพื่อดึงข้อมูล product_type
            products = db.session.query(Product, ProductLot).join(ProductLot, Product.product_id == ProductLot.product_id).filter(Product.product_id == item.product_id).all()

            if products:
                # ตรวจสอบว่าหน่วยที่ถูกเบิกเป็นหน่วยฐานหรือไม่
                if unit_name in ['g', 'mL']:
                    requested_quantity_base = float(item.request_quantity)  # ใช้ค่าเดิมถ้าเป็นหน่วยฐาน
                else:
                    # แปลง requested_quantity_base เป็นหน่วยฐาน (g หรือ mL)
                    requested_quantity_base = convert_to_base_unit(float(item.request_quantity), unit_name, products[0].Product.product_type)
                
                remaining_quantity = Decimal(requested_quantity_base)

                for product, product_lot in products:
                    # แปลง lot_quantity เป็นหน่วยฐานถ้าหากไม่ใช่หน่วยเล็กสุด
                    if product.product_unit in ['g', 'mL']:
                        lot_quantity_base = float(product_lot.lot_quantity)  # ใช้ค่าเดิมถ้าเป็นหน่วยเล็กสุด
                    else:
                        lot_quantity_base = convert_to_base_unit(float(product_lot.lot_quantity), product.product_unit, product.product_type)
                    
                    lot_quantity_base = Decimal(lot_quantity_base)

                    if remaining_quantity <= lot_quantity_base:
                        # หักจำนวนสินค้าที่เบิกออกจากสินค้าจาก lot นี้
                        updated_quantity_base = lot_quantity_base - remaining_quantity

                        # แปลงกลับเป็นหน่วยใหญ่สุดใน lot หรือใช้หน่วยเดิมถ้าเป็นหน่วยฐาน
                        updated_quantity = float(updated_quantity_base) if product.product_unit in ['g', 'mL'] else convert_to_largest_unit(float(updated_quantity_base), product.product_type)[0]

                        # อัปเดตจำนวนสินค้าใน lot โดยไม่เปลี่ยนหน่วย
                        product_lot.lot_quantity = updated_quantity

                        # ลบข้อมูลเมื่อ lot_quantity เป็น 0
                        if product_lot.lot_quantity == 0:
                            db.session.delete(product_lot)
                            db.session.commit()

                        # หักจาก product_quantity ของสินค้าหลักในตาราง products
                        product_quantity_base = convert_to_base_unit(float(product.product_quantity), product.product_unit, product.product_type)
                        updated_product_quantity_base = Decimal(product_quantity_base) - remaining_quantity
                        
                        # แปลงกลับไปยังหน่วยเดิมของ product_unit โดยไม่เปลี่ยนหน่วย
                        updated_product_quantity = float(updated_product_quantity_base) if product.product_unit in ['g', 'mL'] else convert_to_largest_unit(float(updated_product_quantity_base), product.product_type)[0]

                        # อัปเดตจำนวนสินค้าในตาราง products โดยไม่เปลี่ยน product_unit
                        product.product_quantity = updated_product_quantity

                        db.session.commit()
                        break
                    else:
                        remaining_quantity -= lot_quantity_base
                        product_lot.lot_quantity = 0
                        db.session.delete(product_lot)  # ลบข้อมูลเมื่อ lot_quantity เป็น 0
                        db.session.commit()

                        # แปลง product_quantity เป็นหน่วยฐานก่อนหัก โดยไม่เปลี่ยนหน่วย
                        product_quantity_base = convert_to_base_unit(float(product.product_quantity), product.product_unit, product.product_type)
                        updated_product_quantity_base = Decimal(product_quantity_base) - lot_quantity_base

                        # แปลงกลับไปยังหน่วยเดิมของ product_unit โดยไม่เปลี่ยนหน่วย
                        updated_product_quantity = float(updated_product_quantity_base) if product.product_unit in ['g', 'mL'] else convert_to_largest_unit(float(updated_product_quantity_base), product.product_type)[0]

                        # อัปเดตจำนวนสินค้าในตาราง products โดยไม่เปลี่ยน product_unit
                        product.product_quantity = updated_product_quantity

                        db.session.commit()

        # อัปเดตสถานะคำขอเบิกเป็น 'accept'
        req = Request.query.filter_by(request_id=request_id).first()
        req.request_status = 'accept' 
        db.session.commit()

        flash('ยืนยันการเบิกสินค้าสำเร็จ', 'success')
        return redirect(url_for('request.confirm_request'))

    if current_user.employee_position == 'clerical':
        return render_template('clerical/confirm_request.html', requests=requests)
    elif current_user.employee_position == 'keeper':
        return render_template('keeper/history_request.html', requests=requests)

@requestController.route('/request/<string:request_id>/details', methods=['GET'])
@login_required
def request_details(request_id):
    # if current_user.employee_position not in ['clerical', 'keeper']:
    #     flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'danger')
    #     return redirect(url_for('main.index'))
    
    # ดึงรายการสินค้าที่ถูกเบิกตาม request_id
    request = Request.query.filter_by(request_id=request_id).first()
    if not request:
        flash('ไม่พบคำขอเบิกสินค้านี้', 'danger')
        return redirect(url_for('request.confirm_request'))

    # ดึงรายการสินค้าที่เกี่ยวข้องกับคำขอเบิกนี้
    # request_list = RequestList.query.filter_by(request_id=request_id).all()

    request_lists = RequestList.query.filter_by(request_id=request_id).all()
    details = []
    for item in request_lists:
        product = Product.query.filter_by(product_id=item.product_id).first()
        unit = Unit.query.filter_by(unit_id=item.unit_id).first()
        details.append({
            'product': product,
            'unit': unit,
            'request_quantity' : item.request_quantity
        })

    # return render_template('clerical/request_details.html', request=request, request_list=request_list)
    if current_user.employee_position == 'clerical':
        return render_template('clerical/request_details.html', request=request, request_list=details)
    elif current_user.employee_position == 'keeper':
        return render_template('keeper/request_details.html', request=request, request_list=details)
    elif current_user.employee_position == 'worker':
        return render_template('worker/history_request_detail.html', request=request, request_list=details)
    elif current_user.employee_position == 'academic':
        return render_template('academic/history_request_detail.html', request=request, request_list=details)

@requestController.route('/request/reject', methods=['POST'])
@login_required
def reject_request():
    if current_user.employee_position != 'clerical':
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

@requestController.route('/request/cart/cancel', methods=['POST'])
@login_required
def cancel_cart():
    session.pop('cart', None)
    flash('Cart cleared!', 'success')
    return redirect(url_for('request.view_cart'))

@requestController.route('/request/<string:request_id>/confirm', methods=['POST'])
@login_required
def confirm_request_for_wa(request_id):
    request = Request.query.filter_by(request_id=request_id).first()
    if request:
        request.request_status = 'done'
        db.session.commit()
        flash('ยืนยันรับสินค้าสำเร็จ', 'success')
    else:
        flash('ไม่พบคำขอเบิกสินค้านี้', 'danger')
    return redirect(url_for('request.request_details', request_id=request_id))
