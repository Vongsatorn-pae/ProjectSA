from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.audit import Audit
from models.auditList import AuditList
from models.order import Order
from extensions import db
from datetime import date, datetime, timedelta

auditController = Blueprint('audit', __name__)

# ฟังก์ชันตรวจสอบสิทธิ์เพื่อนำไปใช้ใน Controller
def is_clerical():
    return current_user.employee_position == 'clerical'

def format_date_th(date):
    return date.strftime('%d/%m/%Y') if date else None

@auditController.route('/audit/summary', methods=['GET', 'POST'])
@login_required
def audit_summary():
    if current_user.employee_position not in ['keeper', 'clerical']:
        # flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('auth.logout'))

    # ดึงรายการ audit_id และ payment_due_date เรียงจากวันที่ใหม่ขึ้นมาก่อนสำหรับ dropdown
    audit_ids = [
        {'audit_id': audit.audit_id, 'payment_due_date': audit.payment_due_date.strftime("%d/%m/%Y")}
        for audit in Audit.query.with_entities(Audit.audit_id, Audit.payment_due_date, Audit.payment_status)
        .order_by(Audit.payment_due_date.desc())
        .all()
    ]

    # ตั้งค่า selected_audit_id เริ่มต้นเป็น audit_id ล่าสุด
    selected_audit_id = request.form.get('selected_audit_id') or (audit_ids[0]['audit_id'] if audit_ids else None)
    orders_in_audit = []
    total_amount = 0.0
    payment_status = None
    payment_due_date = None
    payment_due_date_str = None

    if selected_audit_id:
        # ดึงข้อมูล audit ที่เกี่ยวข้องกับ audit_id ที่เลือก
        audit_record = Audit.query.get(selected_audit_id)
        if audit_record:
            payment_status = audit_record.payment_status
            payment_due_date = audit_record.payment_due_date.date()
            payment_due_date_str = payment_due_date.strftime("%d/%m/%Y")

        # ดึงรายการ order ที่มี audit_id ตรงกับ audit_id ที่เลือก
        orders_in_audit = db.session.query(Order.order_id, Order.order_date, AuditList.order_amount).join(
            AuditList, AuditList.order_id == Order.order_id
        ).filter(AuditList.audit_id == selected_audit_id).all()
        
        # คำนวณยอดรวมสำหรับ audit_id ที่เลือก
        total_amount = sum(order[2] for order in orders_in_audit if order[2] is not None)

    # Rendering template ตามตำแหน่งของผู้ใช้งาน
    if current_user.employee_position == 'clerical':
        return render_template(
            'clerical/audit_summary.html',
            audit_ids=audit_ids,
            orders_in_audit=orders_in_audit,
            total_amount=total_amount,
            selected_audit_id=selected_audit_id,
            payment_status=payment_status,
            payment_due_date=payment_due_date,
            payment_due_date_str=payment_due_date_str,
            date=date,
            format_date_th=format_date_th
        )
    elif current_user.employee_position == 'keeper':
        return render_template(
            'keeper/audit_summary.html',
            audit_ids=audit_ids,
            orders_in_audit=orders_in_audit,
            total_amount=total_amount,
            selected_audit_id=selected_audit_id,
            payment_status=payment_status,
            payment_due_date=payment_due_date,
            payment_due_date_str=payment_due_date_str,
            format_date_th=format_date_th
        )

# หน้ากรอกราคาสินค้าสำหรับคำสั่งซื้อที่ยังไม่กำหนดราคา
@auditController.route('/audit/add_price', methods=['GET', 'POST'])
@login_required
def add_price():
    if not is_clerical():
        # flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        order_prices = request.form.getlist('order_price')
        order_ids = request.form.getlist('order_id')

        # ตรวจสอบว่า Audit ที่มี payment_due_date ภายใน 70 วัน
        existing_audit = Audit.query.filter(
            Audit.payment_due_date >= datetime.now(),
            Audit.payment_status == False
        ).first()

        # ถ้าไม่มี Audit ที่มี payment_due_date ภายใน 70 วัน ให้สร้างใหม่
        if not existing_audit:
            audit_id = f"AUD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            payment_due_date = datetime.now() + timedelta(days=70)
            new_audit = Audit(audit_id=audit_id, payment_due_date=payment_due_date, payment_status=False)
            db.session.add(new_audit)
            db.session.flush()  # บันทึกการเปลี่ยนแปลงเพื่อให้ audit_id ใหม่ถูกสร้าง
        else:
            audit_id = existing_audit.audit_id  # ใช้ audit_id ที่ยังไม่หมดอายุ

        for order_id, price in zip(order_ids, order_prices):
            if price:
                audit_list_id = f"AL-{order_id}"
                
                # เพิ่มรายการใน audit_list โดยใช้ audit_id ที่ได้มา
                new_audit_list = AuditList(
                    audit_list_id=audit_list_id,
                    audit_id=audit_id,
                    order_id=order_id,
                    order_amount=float(price)
                )
                db.session.add(new_audit_list)
                
                # อัปเดตสถานะของคำสั่งซื้อเป็น done
                order = Order.query.get(order_id)
                order.order_status = 'done'

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
        # flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'danger')
        return redirect(url_for('main.index'))

    audit_record = Audit.query.get(audit_id)
    if audit_record:
        if audit_record.payment_due_date.date() > date.today():
            flash('ยังไม่ถึงวันที่ครบกำหนดชำระ', 'warning')
            return redirect(url_for('audit.audit_summary'))

        audit_record.payment_status = True
        db.session.commit()
        flash('Marked as Paid successfully!', 'success')
    else:
        flash('Audit record not found.', 'danger')

    return redirect(url_for('audit.audit_summary'))
