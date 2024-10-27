from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.audit import Audit
from models.auditList import AuditList
from models.order import Order
from extensions import db
from datetime import datetime, timedelta

auditController = Blueprint('audit', __name__)

# ฟังก์ชันตรวจสอบสิทธิ์เพื่อนำไปใช้ใน Controller
def is_clerical():
    return current_user.employee.employee_position == 'clerical'

@auditController.route('/audit/summary', methods=['GET', 'POST'])
@login_required
def audit_summary():
    if not is_clerical():
        flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'danger')
        return redirect(url_for('main.index'))

    # ดึงรายการ audit_id ทั้งหมดจากตาราง Audit สำหรับ dropdown
    audit_ids = Audit.query.with_entities(Audit.audit_id).all()

    selected_audit_id = request.form.get('selected_audit_id')  # อ่าน audit_id ที่เลือกจาก dropdown
    orders_in_audit = []
    total_amount = 0.0
    payment_status = None
    payment_due_date = None

    if selected_audit_id:
        # ดึงข้อมูล audit ที่เกี่ยวข้องกับ audit_id ที่เลือก
        audit_record = Audit.query.get(selected_audit_id)
        if audit_record:
            payment_status = audit_record.payment_status
            payment_due_date = audit_record.payment_due_date

        # ดึงรายการ order ที่มี audit_id ตรงกับ audit_id ที่เลือก
        orders_in_audit = db.session.query(Order.order_id, Order.order_date, AuditList.order_amount).join(
            AuditList, AuditList.order_id == Order.order_id
        ).filter(AuditList.audit_id == selected_audit_id).all()
        
        # คำนวณยอดรวมสำหรับ audit_id ที่เลือก
        total_amount = sum(order[2] for order in orders_in_audit if order[2] is not None)

    return render_template(
        'clerical/audit_summary.html',
        audit_ids=[audit_id[0] for audit_id in audit_ids],  # ส่ง audit_id ไปยัง dropdown
        orders_in_audit=orders_in_audit,
        total_amount=total_amount,
        selected_audit_id=selected_audit_id,
        payment_status=payment_status,
        payment_due_date=payment_due_date
    )

# หน้ากรอกราคาสินค้าสำหรับคำสั่งซื้อที่ยังไม่กำหนดราคา
@auditController.route('/audit/add_price', methods=['GET', 'POST'])
@login_required
def add_price():
    if not is_clerical():
        flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        order_prices = request.form.getlist('order_price')
        order_ids = request.form.getlist('order_id')

        # ตรวจสอบว่า `Audit` ที่มี `payment_due_date` ภายใน 70 วัน
        existing_audit = Audit.query.filter(
            Audit.payment_due_date >= datetime.now(),
            Audit.payment_status == False
        ).first()

        # ถ้าไม่มี `Audit` ที่มี `payment_due_date` ภายใน 70 วัน ให้สร้างใหม่
        if not existing_audit:
            audit_id = f"AUD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            payment_due_date = datetime.now() + timedelta(days=70)
            new_audit = Audit(audit_id=audit_id, payment_due_date=payment_due_date, payment_status=False)
            db.session.add(new_audit)
            db.session.flush()  # บันทึกการเปลี่ยนแปลงเพื่อให้ `audit_id` ใหม่ถูกสร้าง
        else:
            audit_id = existing_audit.audit_id  # ใช้ `audit_id` ที่ยังไม่หมดอายุ

        for order_id, price in zip(order_ids, order_prices):
            if price:
                audit_list_id = f"AL-{order_id}"
                
                # เพิ่มรายการใน `audit_list` โดยใช้ `audit_id` ที่ได้มา
                new_audit_list = AuditList(
                    audit_list_id=audit_list_id,
                    audit_id=audit_id,
                    order_id=order_id,
                    order_amount=float(price)
                )
                db.session.add(new_audit_list)
        
        db.session.commit()
        flash('บันทึกราคาสำเร็จ', 'success')
        return redirect(url_for('audit.audit_summary'))

    # แสดงรายการที่ต้องการกำหนดราคา
    orders_without_price = Order.query.filter_by(order_status='accept').all()
    orders_to_price = []
    for order in orders_without_price:
        if not AuditList.query.filter_by(order_id=order.order_id).first():
            orders_to_price.append(order)
    return render_template('clerical/add_price.html', orders=orders_to_price)

@auditController.route('/audit/mark_as_paid/<audit_id>', methods=['POST'])
@login_required
def mark_as_paid(audit_id):
    if not is_clerical():
        flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'danger')
        return redirect(url_for('main.index'))

    audit_record = Audit.query.get(audit_id)
    if audit_record:
        audit_record.payment_status = True
        db.session.commit()
        flash('Marked as Paid successfully!', 'success')
    else:
        flash('Audit record not found.', 'danger')

    return redirect(url_for('audit.audit_summary'))
