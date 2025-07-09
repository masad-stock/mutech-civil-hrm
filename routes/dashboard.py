from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import User, Department, Attendance, LeaveRequest, db
from forms.auth_forms import ProfileForm, LeaveRequestForm
from utils.decorators import active_user_required
from datetime import datetime, date, timedelta
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
@active_user_required
def index():
    """Main dashboard for regular users"""
    # Get user's recent attendance
    recent_attendance = Attendance.query.filter_by(
        user_id=current_user.id
    ).order_by(Attendance.date.desc()).limit(5).all()
    
    # Get user's pending leave requests
    pending_leaves = LeaveRequest.query.filter_by(
        user_id=current_user.id,
        status='pending'
    ).order_by(LeaveRequest.created_at.desc()).all()
    
    # Get today's attendance
    today_attendance = Attendance.query.filter_by(
        user_id=current_user.id,
        date=date.today()
    ).first()
    
    # Calculate this month's working hours
    start_of_month = date.today().replace(day=1)
    monthly_attendance = Attendance.query.filter(
        Attendance.user_id == current_user.id,
        Attendance.date >= start_of_month,
        Attendance.date <= date.today()
    ).all()
    
    total_hours = sum(att.hours_worked for att in monthly_attendance)
    
    # Get leave balance
    leave_balance = {
        'annual': current_user.employee_profile.annual_leave_balance if current_user.employee_profile else 21,
        'sick': current_user.employee_profile.sick_leave_balance if current_user.employee_profile else 10
    }
    
    return render_template('dashboard/index.html',
                         recent_attendance=recent_attendance,
                         pending_leaves=pending_leaves,
                         today_attendance=today_attendance,
                         total_hours=total_hours,
                         leave_balance=leave_balance)

@dashboard_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@active_user_required
def profile():
    """User profile management"""
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        current_user.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Your profile has been updated successfully!', 'success')
        return redirect(url_for('dashboard.profile'))
    
    return render_template('dashboard/profile.html', form=form)

@dashboard_bp.route('/attendance')
@login_required
@active_user_required
def attendance():
    """View attendance records"""
    page = request.args.get('page', 1, type=int)
    
    attendance_records = Attendance.query.filter_by(
        user_id=current_user.id
    ).order_by(Attendance.date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Calculate monthly statistics
    current_month = date.today().replace(day=1)
    monthly_stats = db.session.query(
        func.count(Attendance.id).label('total_days'),
        func.sum(
            func.case(
                (Attendance.status == 'present', 1),
                else_=0
            )
        ).label('present_days'),
        func.sum(
            func.case(
                (Attendance.status == 'late', 1),
                else_=0
            )
        ).label('late_days'),
        func.sum(
            func.case(
                (Attendance.status == 'absent', 1),
                else_=0
            )
        ).label('absent_days')
    ).filter(
        Attendance.user_id == current_user.id,
        Attendance.date >= current_month
    ).first()
    
    return render_template('dashboard/attendance.html',
                         attendance_records=attendance_records,
                         monthly_stats=monthly_stats)

@dashboard_bp.route('/leave_requests')
@login_required
@active_user_required
def leave_requests():
    """View leave requests"""
    page = request.args.get('page', 1, type=int)
    
    leave_requests = LeaveRequest.query.filter_by(
        user_id=current_user.id
    ).order_by(LeaveRequest.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('dashboard/leave_requests.html',
                         leave_requests=leave_requests)

@dashboard_bp.route('/request_leave', methods=['GET', 'POST'])
@login_required
@active_user_required
def request_leave():
    """Submit leave request"""
    form = LeaveRequestForm()
    
    if form.validate_on_submit():
        # Calculate days requested
        start_date = datetime.strptime(form.start_date.data, '%Y-%m-%d').date()
        end_date = datetime.strptime(form.end_date.data, '%Y-%m-%d').date()
        days_requested = (end_date - start_date).days + 1
        
        # Validate dates
        if start_date < date.today():
            flash('Start date cannot be in the past.', 'error')
            return render_template('dashboard/request_leave.html', form=form)
        
        if end_date < start_date:
            flash('End date cannot be before start date.', 'error')
            return render_template('dashboard/request_leave.html', form=form)
        
        # Check leave balance
        if form.leave_type.data == 'annual':
            available_balance = current_user.employee_profile.annual_leave_balance if current_user.employee_profile else 21
            if days_requested > available_balance:
                flash(f'Insufficient annual leave balance. Available: {available_balance} days', 'error')
                return render_template('dashboard/request_leave.html', form=form)
        
        leave_request = LeaveRequest(
            user_id=current_user.id,
            leave_type=form.leave_type.data,
            start_date=start_date,
            end_date=end_date,
            days_requested=days_requested,
            reason=form.reason.data
        )
        
        db.session.add(leave_request)
        db.session.commit()
        
        flash('Your leave request has been submitted successfully!', 'success')
        return redirect(url_for('dashboard.leave_requests'))
    
    return render_template('dashboard/request_leave.html', form=form)

@dashboard_bp.route('/clock_in')
@login_required
@active_user_required
def clock_in():
    """Clock in for the day"""
    today = date.today()
    existing_attendance = Attendance.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()
    
    if existing_attendance and existing_attendance.check_in:
        flash('You have already clocked in today.', 'warning')
    else:
        if not existing_attendance:
            existing_attendance = Attendance(
                user_id=current_user.id,
                date=today
            )
            db.session.add(existing_attendance)
        
        existing_attendance.check_in = datetime.now().time()
        existing_attendance.status = 'present'
        
        # Check if late (assuming 8:00 AM is start time)
        if existing_attendance.check_in > datetime.strptime('08:00', '%H:%M').time():
            existing_attendance.status = 'late'
        
        db.session.commit()
        flash('Clocked in successfully!', 'success')
    
    return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/clock_out')
@login_required
@active_user_required
def clock_out():
    """Clock out for the day"""
    today = date.today()
    attendance = Attendance.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()
    
    if not attendance or not attendance.check_in:
        flash('You must clock in first.', 'error')
    elif attendance.check_out:
        flash('You have already clocked out today.', 'warning')
    else:
        attendance.check_out = datetime.now().time()
        db.session.commit()
        flash('Clocked out successfully!', 'success')
    
    return redirect(url_for('dashboard.index'))
