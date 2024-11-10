from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.product import Product
from models.productList import ProductList
from models.productLot import ProductLot
from models.product import Product
from models.order import Order
from models.orderList import OrderList
from models.unit import Unit
# from utils.conversion import convert_to_base_unit, convert_to_largest_unit
from extensions import db
from datetime import datetime

stockController = Blueprint('stock', __name__)

def convert_to_base_unit(quantity, unit, product_type):
    """แปลงหน่วยสินค้าเป็นหน่วยเล็กที่สุด (g สำหรับ Food และ mL สำหรับ Chemical)"""
    if product_type == 'Food':
        if unit == 'Kg':
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
    """เปลี่ยนหน่วยเป็นหน่วยใหญ่ที่สุด (Kg สำหรับ Food และ L สำหรับ Chemical)"""
    if product_type == 'Food':
        if quantity >= 1000:
            return quantity / 1000, 'Kg'  # แปลงกลับเป็น kg ถ้าจำนวน >= 1000g
        else:
            return quantity, 'g'  # แสดงเป็น g ถ้าน้อยกว่า 1000g

    elif product_type == 'Chemical':
        if quantity >= 1000:
            return quantity / 1000, 'L'  # แปลงกลับเป็น L ถ้าจำนวน >= 1000mL
        else:
            return quantity, 'mL'  # แสดงเป็น mL ถ้าน้อยกว่า 1000mL

    else:
        raise ValueError("Unknown product type")

def generate_product_id(product_type):
    # กำหนด prefix ตามประเภทสินค้า
    prefix = 'F' if product_type == 'Food' else 'C'
    
    # ดึง product_id ล่าสุดที่ขึ้นต้นด้วย prefix จากฐานข้อมูล
    last_product = Product.query.filter(Product.product_id.like(f"{prefix}%")).order_by(Product.product_id.desc()).first()
    
    # หากมี product_id ที่สร้างไว้ก่อนหน้า ให้ดึงหมายเลขแล้วบวกเพิ่ม
    if last_product:
        last_id_num = int(last_product.product_id[1:])  # ตัดตัวอักษรตัวแรกออกแล้วแปลงเป็นเลข
        new_id_num = last_id_num + 1
    else:
        new_id_num = 1  # หากยังไม่มี id ในประเภทนั้น ให้เริ่มต้นจาก 1

    # สร้าง product_id ใหม่ โดยเพิ่มเลข 3 หลักต่อท้าย prefix
    return f"{prefix}{new_id_num:03}"

# Route สำหรับดูรายการสินค้าในสต็อก
@stockController.route('/stock')
@login_required
def view_stock():
    if current_user.employee_position not in ['keeper', 'clerical']:
        # flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('auth.logout'))

    # stock_data = db.session.query(
    #     ProductList.product_id,
    #     ProductList.product_name,
    #     ProductList.product_image,
    #     Product.product_quantity,
    #     Product.product_unit,
    #     ProductList.product_type
    # ).join(Product, Product.product_id == ProductList.product_id).all()
    stock_data = db.session.query(
        Product.product_id,
        Product.product_name,
        Product.product_image,
        Product.product_quantity,
        Product.product_unit,
        Product.product_type
    ).all()

    # รวมสินค้าโดย product_id
    # combined_stock = {}
    # for item in stock_data:
    #     base_quantity = convert_to_base_unit(item.product_quantity, item.product_unit, item.product_type)

    #     if item.product_id in combined_stock:
    #         combined_stock[item.product_id]['total_quantity'] += base_quantity
    #     else:
    #         combined_stock[item.product_id] = {
    #             'product_name': item.product_name,
    #             'product_image': item.product_image,
    #             'total_quantity': base_quantity,
    #             'product_type': item.product_type
    #         }

    # # แปลงหน่วยกลับเป็นหน่วยใหญ่ที่สุด
    # for product_id, data in combined_stock.items():
    #     total_quantity, unit = convert_to_largest_unit(data['total_quantity'], data['product_type'])
    #     data['total_quantity'] = total_quantity
    #     data['unit'] = unit

    # if current_user.employee_position == 'clerical':
    #     return render_template('clerical/view_stock.html', products=combined_stock.values())
    # elif current_user.employee_position == 'keeper':
    #     return render_template('keeper/view_stock.html', products=combined_stock.values())

    if current_user.employee_position == 'clerical':
        return render_template('clerical/view_stock.html', products=stock_data)
    elif current_user.employee_position == 'keeper':
        return render_template('keeper/view_stock.html', products=stock_data)

# Route สำหรับเพิ่มสินค้าใหม่
@stockController.route('/stock/add', methods=['GET', 'POST'])
@login_required
def add_stock():
    if current_user.employee_position != 'clerical':
        # flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('auth.logout'))
    
    products = Product.query.all()
    units = Unit.query.all()
    unit_list = [
        {"unit_id": unit.unit_id, "unit_name": unit.unit_name, "product_type": unit.product_type or ""}
        for unit in units if unit.unit_name is not None
    ]

    # ลิสต์ของรูปภาพที่ให้เลือก
    image_options = [
        {"url": "https://kasets.art/51kGYq", "name": "Food"},
        {"url": "https://kasets.art/HtBpeI", "name": "Chemical"}
    ]

    if request.method == 'POST':
        product_type = request.form['product_type']
        product_name = request.form['product_name']
        product_unit = request.form['product_unit']
        
        # สร้าง product_id โดยใช้ฟังก์ชัน generate_product_id ถ้าไม่มีการกรอก product_id
        product_id = request.form['product_id'] or generate_product_id(product_type)
        
        # ถ้าไม่ได้ใส่ product_quantity หรือ threshold ให้ตั้งค่าเริ่มต้นเป็น 0
        product_quantity = request.form.get('product_quantity', 0) or 0
        threshold = request.form.get('threshold', 0) or 2000
        product_image = request.form['product_image']

        new_product = Product(
            product_id=product_id,
            product_name=product_name,
            product_type=product_type,
            product_unit=product_unit,
            product_quantity=product_quantity,
            threshold=threshold,
            product_image=product_image
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('stock.view_stock'))

    return render_template('clerical/add_stock.html', product_lists=products, units=unit_list, image_options=image_options)

def get_stock_alerts(limit=None):
    stock_alerts = []

    products = Product.query.all()

    for product in products:
        stock_products = Product.query.filter_by(product_id=product.product_id).all()

        total_quantity_in_stock = sum(
            convert_to_base_unit(
                stock_product.product_quantity,
                stock_product.product_unit,
                product.product_type
            ) for stock_product in stock_products
        )

        if total_quantity_in_stock <= float(product.threshold):
            alert = {
                'product_id': product.product_id,
                'product_name': product.product_name,
                'total_quantity_in_stock': total_quantity_in_stock,
                'threshold': float(product.threshold),
                'unit_name': 'g' if product.product_type == 'Food' else 'mL',
                'image_url': product.product_image
            }
            stock_alerts.append(alert)

    return stock_alerts

@stockController.route('/stock/alert')
@login_required
def stock_alert():
    stock_data = get_stock_alerts()
    return render_template('dashboard.html', stock_alerts=stock_data)

# @stockController.route('/product_detail/<product_id>')
# @login_required
# def product_detail(product_id):
#     product = ProductList.query.filter_by(product_id=product_id).first_or_404()
#     units = Unit.query.all()

#     return render_template('keeper/product_detail.html', product=product, units=units)

@stockController.route('/stock/<product_id>/lots', methods=['GET'])
@login_required
def view_stock_lot(product_id):
    lots = ProductLot.query.filter_by(product_id=product_id).all()
    
    formatted_lots = []
    for lot in lots:
        lot_date = (
            datetime.strptime(lot.lot_date, "%Y-%m-%d").strftime("%d/%m/%Y")
            if isinstance(lot.lot_date, str) else
            lot.lot_date.strftime("%d/%m/%Y") if lot.lot_date else None
        )
        lot_exp = (
            datetime.strptime(lot.lot_exp, "%Y-%m-%d").strftime("%d/%m/%Y")
            if isinstance(lot.lot_exp, str) else
            lot.lot_exp.strftime("%d/%m/%Y") if lot.lot_exp else None
        )

        lot_data = {
            'lot_id': lot.lot_id,
            'lot_date': lot_date,
            'lot_exp': lot_exp,
        }
        formatted_lots.append(lot_data)

    # return render_template('keeper/view_stock_lot.html', product_id=product_id, lots=formatted_lots)
    if current_user.employee_position == 'clerical':
        return render_template('clerical/view_stock_lot.html', product_id=product_id, lots=formatted_lots)
    elif current_user.employee_position == 'keeper':
        return render_template('keeper/view_stock_lot.html', product_id=product_id, lots=formatted_lots)

@stockController.route('/stock/lot/<lot_id>', methods=['GET'])
@login_required
def view_stock_details(lot_id):
    lot = ProductLot.query.filter_by(lot_id=lot_id).first_or_404()
    
    lot_date = lot.lot_date.strftime("%d/%m/%Y") if lot.lot_date else None
    lot_exp = lot.lot_exp.strftime("%d/%m/%Y") if lot.lot_exp else None

    # return render_template('keeper/view_stock_details.html', lot=lot, lot_date=lot_date, lot_exp=lot_exp)
    if current_user.employee_position == 'clerical':
        return render_template('clerical/view_stock_details.html', lot=lot, lot_date=lot_date, lot_exp=lot_exp)
    elif current_user.employee_position == 'keeper':
        return render_template('keeper/view_stock_details.html', lot=lot, lot_date=lot_date, lot_exp=lot_exp)
