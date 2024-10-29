from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.productList import ProductList
from models.productLot import ProductLot
from models.product import Product
from models.order import Order
from models.orderList import OrderList
from models.unit import Unit
# from utils.conversion import convert_to_base_unit, convert_to_largest_unit
from extensions import db

stockController = Blueprint('stock', __name__)

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
    elif product_type == 'Liquid' and unit == 'L':
        return quantity * 1000  # Convert liters to milliliters
    return quantity  # No conversion needed for other units

# Route สำหรับดูรายการสินค้าในสต็อก
@stockController.route('/stock')
@login_required
def view_stock():
    # ตรวจสอบบทบาทว่าผู้ใช้ต้องเป็นธุรการ (clerical) เท่านั้น
    # if current_user.employee.employee_position != 'clerical':
    if current_user.employee.employee_position not in ['keeper', 'clerical']:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('auth.logout'))

    # ดึงข้อมูลจาก product_lists และ products
    stock_data = db.session.query(
        ProductList.product_id,
        ProductList.product_name,
        ProductList.product_image,
        Product.product_quantity,
        Product.product_unit,
        ProductList.product_type
    ).join(Product, Product.product_id == ProductList.product_id).all()

    # รวมสินค้าโดย product_id
    combined_stock = {}
    for item in stock_data:
        base_quantity = convert_to_base_unit(item.product_quantity, item.product_unit, item.product_type)

        if item.product_id in combined_stock:
            combined_stock[item.product_id]['total_quantity'] += base_quantity
        else:
            combined_stock[item.product_id] = {
                'product_name': item.product_name,
                'product_image': item.product_image,
                'total_quantity': base_quantity,
                'product_type': item.product_type
            }

    # แปลงหน่วยกลับเป็นหน่วยใหญ่ที่สุด
    for product_id, data in combined_stock.items():
        total_quantity, unit = convert_to_largest_unit(data['total_quantity'], data['product_type'])
        data['total_quantity'] = total_quantity
        data['unit'] = unit
    if current_user.employee.employee_position == 'clerical':
        return render_template('clerical/view_stock.html', products=combined_stock.values())
    elif current_user.employee.employee_position == 'keeper':
        return render_template('keeper/view_stock.html', products=combined_stock.values())

# Route สำหรับเพิ่มสินค้าใหม่
@stockController.route('/stock/add', methods=['GET', 'POST'])
@login_required
def add_stock():
    # ตรวจสอบบทบาทว่าผู้ใช้ต้องเป็นธุรการ (clerical) เท่านั้น
    if current_user.employee.employee_position != 'clerical':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('auth.logout'))
    
    product_lists = ProductList.query.all()

    # ดึง lot ที่เกี่ยวข้องกับ order ที่มี order_status = True
    product_lots = ProductLot.query.join(OrderList, ProductLot.lot_id == OrderList.lot_id)\
                                   .join(Order, OrderList.order_id == Order.order_id)\
                                   .filter(Order.order_status == 'accept').all()

    # ดึงข้อมูล units ทั้งหมดและแปลงเป็น dict
    units = Unit.query.all()
    unit_list = [
        {"unit_id": unit.unit_id, "unit_name": unit.unit_name, "product_type": unit.product_type or ""}
        for unit in units if unit.unit_name is not None
    ]

    if request.method == 'POST':
        product_id = request.form['product_id']  # ดึง id ของสินค้าที่เลือกจาก dropdown
        lot_id = request.form['lot_id']  # ดึง lot_id จาก dropdown
        product_quantity = request.form['product_quantity']
        product_unit = request.form['product_unit']
        product_exp = request.form['product_exp']  # ดึงวันที่หมดอายุจากฟอร์ม

        # เพิ่มข้อมูลสินค้าพร้อมข้อมูลล็อตเข้าสู่ฐานข้อมูล
        new_product = Product(
            product_id=product_id,  # ใส่ product_id เท่านั้น
            lot_id=lot_id,  # lot_id จาก product_lots
            product_quantity=product_quantity,
            product_unit=product_unit,
            product_exp=product_exp  # เพิ่มวันที่หมดอายุ
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('stock.view_stock'))

    return render_template('clerical/add_stock.html', product_lists=product_lists, product_lots=product_lots, units=unit_list)

def get_stock_alerts(limit=None):
    """Fetch stock alerts for products below the threshold."""
    stock_alerts = []

    # Fetch all products from ProductList
    product_list = ProductList.query.all()

    for product in product_list:
        # Fetch all stock entries with the same product_id
        stock_products = Product.query.filter_by(product_id=product.product_id).all()

        total_quantity_in_stock = sum(
            convert_to_base_unit1(
                stock_product.product_quantity,
                stock_product.product_unit,
                product.product_type
            ) for stock_product in stock_products
        )

        # Add to alerts if total quantity <= threshold
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

    # Ensure no limit is applied unintentionally
    return stock_alerts

@stockController.route('/stock/alert')
@login_required
def stock_alert():
    """Render the stock alert page."""
    stock_data = get_stock_alerts()  # Fetch all alerts
    return render_template('dashboard.html', stock_alerts=stock_data)


@stockController.route('/product_detail/<product_id>')
@login_required
def product_detail(product_id):
    product = ProductList.query.filter_by(product_id=product_id).first_or_404()
    units = Unit.query.all()  # Fetch units if required

    return render_template('keeper/product_detail.html', product=product, units=units)
