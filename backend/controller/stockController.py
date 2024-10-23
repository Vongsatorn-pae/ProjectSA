from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.productList import ProductList
from models.productLot import ProductLot
from models.product import Product
from models.unit import Unit
from utils.conversion import convert_to_base_unit, convert_to_largest_unit
from extensions import db

stockController = Blueprint('stock', __name__)

# Route สำหรับดูรายการสินค้าในสต็อก
@stockController.route('/stock')
@login_required
def view_stock():
    # ตรวจสอบบทบาทว่าผู้ใช้ต้องเป็นธุรการ (clerical) เท่านั้น
    if current_user.employee.employee_position != 'clerical':
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

    return render_template('clerical/view_stock.html', products=combined_stock.values())

# Route สำหรับเพิ่มสินค้าใหม่
@stockController.route('/stock/add', methods=['GET', 'POST'])
@login_required
def add_stock():
    # ตรวจสอบบทบาทว่าผู้ใช้ต้องเป็นธุรการ (clerical) เท่านั้น
    if current_user.employee.employee_position != 'clerical':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('auth.logout'))
    
    product_lists = ProductList.query.all()
    product_lots = ProductLot.query.all()

    if request.method == 'POST':
        product_id = request.form['product_id']  # ดึง id ของสินค้าที่เลือกจาก dropdown
        lot_id = request.form['lot_id']  # ดึง lot_id จาก dropdown
        product_quantity = request.form['product_quantity']
        product_unit = request.form['product_unit']

        # ดึงข้อมูลสินค้าจาก product_lists
        selected_product = ProductList.query.filter_by(product_id=product_id).first()

        # เพิ่มข้อมูลสินค้าพร้อมข้อมูลล็อตเข้าสู่ฐานข้อมูล
        new_product = Product(
            product_id=selected_product.product_id,  # product_id จาก product_lists
            product_name=selected_product.product_name,  # ใช้ชื่อจาก product_lists
            product_type=selected_product.product_type,  # ใช้ประเภทจาก product_lists
            lot_id=lot_id,  # lot_id จาก product_lots
            product_quantity=product_quantity,
            product_unit=product_unit,
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('stock.view_stock'))

    return render_template('clerical/add_stock.html', product_lists=product_lists, product_lots=product_lots)

@stockController.route('/stock/alert')
@login_required
def stock_alert():
    if current_user.employee.employee_position != 'keeper':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))

    """แสดงรายการสินค้าที่ใกล้จะหมดจากสต็อก"""
    stock_alerts = []

    # ดึงรายการสินค้าทั้งหมดจากตาราง product_lists
    product_list = ProductList.query.all()

    for product in product_list:
        # ดึงข้อมูลสินค้าทั้งหมดที่ตรงกับ product_id จากตาราง products (ทุก lot)
        stock_products = Product.query.filter_by(product_id=product.product_id).all()

        total_quantity_in_stock = 0  # เก็บปริมาณสินค้าทั้งหมดจากทุก lot

        # รวมจำนวนสินค้าจากทุก lot
        for stock_product in stock_products:
            # แปลงหน่วยสินค้าเป็นหน่วยเล็กที่สุด (g หรือ mL)
            total_quantity_in_stock += convert_to_base_unit(
                stock_product.product_quantity, 
                stock_product.product_unit,  # หน่วยสินค้า
                product.product_type  # ประเภทสินค้า
            )

        # ตรวจสอบว่าปริมาณสินค้าทั้งหมดจากทุก lot น้อยกว่า threshold หรือไม่
        if total_quantity_in_stock < product.threshold:
            stock_alerts.append({
                'product_name': product.product_name,
                'total_quantity_in_stock': total_quantity_in_stock,  # ปริมาณคงเหลือรวมจากทุก lot
                'threshold': product.threshold,
                'product_type': product.product_type,
                'unit_name': 'g' if product.product_type == 'Food' else 'mL'  # หน่วยที่แสดงใน stock_alert
            })

    return render_template('keeper/stock_alert.html', products=stock_alerts)
