from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import User, Payment, Payroll, db
from utils.decorators import admin_required, permission_required
from utils.mpesa import MPESAClient, process_mpesa_callback
from datetime import datetime, date
from decimal import Decimal
import json

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/')
@login_required
@permission_required('payments.read')
def index():
    """Payment dashboard"""
    page = request.args.get('page', 1, type=int)
    
    # Filter payments based on user role
    if current_user.has_role('admin') or current_user.has_permission('payments.view_all'):
        payments = Payment.query.order_by(Payment.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
    else:
        payments = Payment.query.filter_by(user_id=current_user.id).order_by(
            Payment.created_at.desc()
        ).paginate(page=page, per_page=20, error_out=False)
    
    # Payment statistics
    total_payments = Payment.query.filter_by(status='completed').count()
    pending_payments = Payment.query.filter_by(status='pending').count()
    failed_payments = Payment.query.filter_by(status='failed').count()
    
    return render_template('payments/index.html',
                         payments=payments,
                         total_payments=total_payments,
                         pending_payments=pending_payments,
                         failed_payments=failed_payments)

@payments_bp.route('/new', methods=['GET', 'POST'])
@login_required
@permission_required('payments.create')
def new_payment():
    """Create new payment"""
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        payment_type = request.form.get('payment_type')
        amount = request.form.get('amount')
        payment_method = request.form.get('payment_method')
        phone_number = request.form.get('phone_number')
        description = request.form.get('description')
        
        # Validation
        if not all([user_id, payment_type, amount, payment_method]):
            flash('All required fields must be filled.', 'error')
            return redirect(url_for('payments.new_payment'))
        
        try:
            amount = Decimal(amount)
            if amount <= 0:
                flash('Amount must be greater than zero.', 'error')
                return redirect(url_for('payments.new_payment'))
        except (ValueError, TypeError):
            flash('Invalid amount format.', 'error')
            return redirect(url_for('payments.new_payment'))
        
        # Create payment record
        payment = Payment(
            user_id=user_id,
            payment_type=payment_type,
            amount=amount,
            payment_method=payment_method,
            phone_number=phone_number,
            description=description,
            processed_by=current_user.id
        )
        
        db.session.add(payment)
        db.session.flush()  # Get payment ID
        
        # Process MPESA payment if selected
        if payment_method == 'mpesa' and phone_number:
            mpesa_client = MPESAClient()
            result = mpesa_client.stk_push(
                phone_number=phone_number,
                amount=amount,
                account_reference=f"PAY{payment.id:06d}",
                transaction_desc=f"{payment_type} payment for {payment.user.full_name}"
            )
            
            if result['success']:
                payment.checkout_request_id = result.get('checkout_request_id')
                payment.merchant_request_id = result.get('merchant_request_id')
                payment.status = 'pending'
                flash('MPESA payment initiated. Please check your phone for payment prompt.', 'info')
            else:
                payment.status = 'failed'
                flash(f'MPESA payment failed: {result["message"]}', 'error')
        else:
            # For non-MPESA payments, mark as pending for manual processing
            payment.status = 'pending'
            flash('Payment created successfully. Manual processing required.', 'success')
        
        db.session.commit()
        return redirect(url_for('payments.view_payment', payment_id=payment.id))
    
    # GET request - show form
    users = User.query.filter_by(is_active=True).order_by(User.first_name).all()
    return render_template('payments/new_payment.html', users=users)

@payments_bp.route('/<int:payment_id>')
@login_required
@permission_required('payments.read')
def view_payment(payment_id):
    """View payment details"""
    payment = Payment.query.get_or_404(payment_id)
    
    # Check if user can view this payment
    if not (current_user.has_role('admin') or 
            current_user.has_permission('payments.view_all') or 
            payment.user_id == current_user.id):
        flash('Access denied.', 'error')
        return redirect(url_for('payments.index'))
    
    return render_template('payments/view_payment.html', payment=payment)

@payments_bp.route('/<int:payment_id>/approve')
@login_required
@permission_required('payments.approve')
def approve_payment(payment_id):
    """Approve payment"""
    payment = Payment.query.get_or_404(payment_id)
    
    if payment.status != 'pending':
        flash('Only pending payments can be approved.', 'error')
        return redirect(url_for('payments.view_payment', payment_id=payment_id))
    
    payment.status = 'completed'
    payment.transaction_date = datetime.utcnow()
    payment.processed_by = current_user.id
    
    db.session.commit()
    
    flash('Payment approved successfully.', 'success')
    return redirect(url_for('payments.view_payment', payment_id=payment_id))

@payments_bp.route('/<int:payment_id>/reject')
@login_required
@permission_required('payments.approve')
def reject_payment(payment_id):
    """Reject payment"""
    payment = Payment.query.get_or_404(payment_id)
    
    if payment.status != 'pending':
        flash('Only pending payments can be rejected.', 'error')
        return redirect(url_for('payments.view_payment', payment_id=payment_id))
    
    payment.status = 'failed'
    payment.processed_by = current_user.id
    
    db.session.commit()
    
    flash('Payment rejected.', 'warning')
    return redirect(url_for('payments.view_payment', payment_id=payment_id))

@payments_bp.route('/mpesa/callback', methods=['POST'])
def mpesa_callback():
    """Handle MPESA callback"""
    try:
        callback_data = request.get_json()
        result = process_mpesa_callback(callback_data)
        
        if result['success']:
            # Find payment by checkout_request_id
            payment = Payment.query.filter_by(
                checkout_request_id=result['checkout_request_id']
            ).first()
            
            if payment:
                payment.status = 'completed'
                payment.mpesa_receipt_number = result['payment_details'].get('receipt_number')
                payment.transaction_date = datetime.utcnow()
                
                db.session.commit()
                
                print(f"Payment {payment.id} completed successfully via MPESA")
            else:
                print(f"Payment not found for checkout_request_id: {result['checkout_request_id']}")
        else:
            # Handle failed payment
            payment = Payment.query.filter_by(
                checkout_request_id=result['checkout_request_id']
            ).first()
            
            if payment:
                payment.status = 'failed'
                db.session.commit()
                
                print(f"Payment {payment.id} failed: {result['message']}")
        
        return jsonify({'ResultCode': 0, 'ResultDesc': 'Success'})
    
    except Exception as e:
        print(f"Error processing MPESA callback: {e}")
        return jsonify({'ResultCode': 1, 'ResultDesc': 'Error processing callback'})

@payments_bp.route('/mpesa/timeout', methods=['POST'])
def mpesa_timeout():
    """Handle MPESA timeout"""
    try:
        timeout_data = request.get_json()
        print(f"MPESA timeout received: {timeout_data}")
        
        return jsonify({'ResultCode': 0, 'ResultDesc': 'Success'})
    
    except Exception as e:
        print(f"Error processing MPESA timeout: {e}")
        return jsonify({'ResultCode': 1, 'ResultDesc': 'Error processing timeout'})

@payments_bp.route('/mpesa/result', methods=['POST'])
def mpesa_result():
    """Handle MPESA B2C result"""
    try:
        result_data = request.get_json()
        print(f"MPESA B2C result received: {result_data}")
        
        return jsonify({'ResultCode': 0, 'ResultDesc': 'Success'})
    
    except Exception as e:
        print(f"Error processing MPESA result: {e}")
        return jsonify({'ResultCode': 1, 'ResultDesc': 'Error processing result'})

@payments_bp.route('/payroll')
@login_required
@permission_required('payments.read')
def payroll():
    """Payroll management"""
    page = request.args.get('page', 1, type=int)
    month = request.args.get('month', date.today().month, type=int)
    year = request.args.get('year', date.today().year, type=int)
    
    # Filter payroll records
    if current_user.has_role('admin') or current_user.has_permission('payments.view_all'):
        payroll_records = Payroll.query.filter_by(
            month=month, year=year
        ).order_by(Payroll.user_id).paginate(
            page=page, per_page=20, error_out=False
        )
    else:
        payroll_records = Payroll.query.filter_by(
            user_id=current_user.id, month=month, year=year
        ).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('payments/payroll.html',
                         payroll_records=payroll_records,
                         month=month,
                         year=year)

@payments_bp.route('/payroll/generate/<int:month>/<int:year>')
@login_required
@admin_required
def generate_payroll(month, year):
    """Generate payroll for all active employees"""
    # Check if payroll already exists for this month/year
    existing_payroll = Payroll.query.filter_by(month=month, year=year).first()
    if existing_payroll:
        flash(f'Payroll for {month}/{year} already exists.', 'warning')
        return redirect(url_for('payments.payroll', month=month, year=year))
    
    # Get all active employees
    employees = User.query.filter_by(is_active=True).all()
    
    for employee in employees:
        if employee.salary:
            payroll = Payroll(
                user_id=employee.id,
                month=month,
                year=year,
                basic_salary=employee.salary,
                allowances=0,  # Can be customized
                overtime_hours=0,
                overtime_rate=0
            )
            
            # Calculate tax and deductions (simplified)
            payroll.tax_deduction = payroll.basic_salary * Decimal('0.1')  # 10% tax
            payroll.nhif_deduction = Decimal('500')  # Fixed NHIF
            payroll.nssf_deduction = Decimal('400')  # Fixed NSSF
            
            payroll.calculate_totals()
            
            db.session.add(payroll)
    
    db.session.commit()
    
    flash(f'Payroll generated successfully for {month}/{year}.', 'success')
    return redirect(url_for('payments.payroll', month=month, year=year))
