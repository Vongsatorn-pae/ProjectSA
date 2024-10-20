from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.productList import ProductList
from models.productLot import ProductLot
from models.product import Product
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

    # ดึงข้อมูลสินค้าทั้งหมดจากฐานข้อมูล
    products = Product.query.all()
    return render_template('clerical/view_stock.html', products=products)

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

    # ดึงสินค้าที่จำนวนในสต็อกต่ำกว่า threshold
    low_stock_products = Product.query.filter(Product.product_quantity < ProductList.threshold).all()

    return render_template('keeper/stock_alert.html', products=low_stock_products)
