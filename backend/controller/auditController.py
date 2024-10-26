from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.audit import Audit
from models.auditList import AuditList
from models.order import Order
from extensions import db
from datetime import datetime, timedelta

auditController = Blueprint('audit', __name__)

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.audit import Audit
from models.auditList import AuditList
from models.order import Order
from extensions import db
from datetime import datetime, timedelta

auditController = Blueprint('audit', __name__)

@auditController.route('/audit/create', methods=['GET', 'POST'])
@login_required
def create_audit():
    if current_user.employee.employee_position != 'clerical':
        flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'danger')
        return redirect(url_for('main.index'))

    # กรองรายการ order ที่มีสถานะ 'accept' เท่านั้น
    orders = Order.query.filter(Order.order_status == 'accept').all()

    if request.method == 'POST':
        # สร้าง audit ใหม่
        audit_id = f"AUD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        payment_due_date = datetime.now() + timedelta(days=70)
        new_audit = Audit(audit_id=audit_id, payment_due_date=payment_due_date)
        db.session.add(new_audit)

        # เพิ่มข้อมูล order ที่มีสถานะ accept ลงใน audit_list พร้อมระบุราคา
        for order in orders:
            order_id = order.order_id
            order_amount = request.form.get(f'order_amount_{order_id}', type=float)

            if order_amount is not None:
                audit_list = AuditList(
                    audit_list_id=f"AL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{order_id}",
                    audit_id=audit_id,
                    order_id=order_id,
                    order_amount=order_amount
                )
                db.session.add(audit_list)

        db.session.commit()
        flash('สร้างรายการตรวจสอบสำเร็จแล้ว!', 'success')
        return redirect(url_for('audit.view_audit_history'))

    return render_template('clerical/create_audit.html', orders=orders)

@auditController.route('/audit/history', methods=['GET'])
@login_required
def view_audit_history():
    if current_user.employee.employee_position != 'clerical':
        flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'danger')
        return redirect(url_for('main.index'))

    audits = Audit.query.all()
    return render_template('clerical/audit_history.html', audits=audits)
