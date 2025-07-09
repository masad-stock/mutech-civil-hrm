from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import User, Department, Role, Permission, Attendance, LeaveRequest, Employee, db
from forms.auth_forms import RegistrationForm, DepartmentForm
from utils.decorators import admin_required
from datetime import datetime, date, timedelta
from sqlalchemy import func, desc
import calendar

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with system overview"""
    # Get system statistics
    total_users = User.query.filter_by(is_active=True).count()
    total_departments = Department.query.filter_by(is_active=True).count()
    
    # Today's attendance
    today = date.today()
    today_attendance = db.session.query(
        func.count(Attendance.id).label('total'),
        func.sum(func.case((Attendance.status == 'present', 1), else_=0)).label('present'),
        func.sum(func.case((Attendance.status == 'late', 1), else_=0)).label('late'),
        func.sum(func.case((Attendance.status == 'absent', 1), else_=0)).label('absent')
    ).filter(Attendance.date == today).first()
    
    # Pending leave requests
    pending_leaves = LeaveRequest.query.filter_by(status='pending').count()
    
    # Recent activities (last 10 users created)
    recent_users = User.query.order_by(desc(User.created_at)).limit(5).all()
    
    # Department statistics
    dept_stats = db.session.query(
        Department.name,
        func.count(User.id).label('employee_count')
    ).join(User).filter(
        User.is_active == True,
        Department.is_active == True
    ).group_by(Department.id, Department.name).all()
    
    # Monthly attendance trend (last 6 months)
    monthly_attendance = []
    for i in range(6):
        month_date = (date.today().replace(day=1) - timedelta(days=i*30))
        month_start = month_date.replace(day=1)
        if month_date.month == 12:
            month_end = month_date.replace(year=month_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_date.replace(month=month_date.month + 1, day=1) - timedelta(days=1)
        
        attendance_count = Attendance.query.filter(
            Attendance.date >= month_start,
            Attendance.date <= month_end,
            Attendance.status == 'present'
        ).count()
        
        monthly_attendance.append({
            'month': calendar.month_name[month_date.month],
            'count': attendance_count
        })
    
    monthly_attendance.reverse()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_departments=total_departments,
                         today_attendance=today_attendance,
                         pending_leaves=pending_leaves,
                         recent_users=recent_users,
                         dept_stats=dept_stats,
                         monthly_attendance=monthly_attendance)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """User management"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    department_filter = request.args.get('department', '', type=str)
    
    query = User.query
    
    if search:
        query = query.filter(
            db.or_(
                User.first_name.contains(search),
                User.last_name.contains(search),
                User.email.contains(search),
                User.employee_id.contains(search)
            )
        )
    
    if department_filter:
        query = query.filter(User.department_id == department_filter)
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    departments = Department.query.filter_by(is_active=True).all()
    
    return render_template('admin/users.html',
                         users=users,
                         departments=departments,
                         search=search,
                         department_filter=department_filter)

@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """User detail view"""
    user = User.query.get_or_404(user_id)
    
    # Get user's recent attendance
    recent_attendance = Attendance.query.filter_by(
        user_id=user.id
    ).order_by(desc(Attendance.date)).limit(10).all()
    
    # Get user's leave requests
    leave_requests = LeaveRequest.query.filter_by(
        user_id=user.id
    ).order_by(desc(LeaveRequest.created_at)).limit(5).all()
    
    return render_template('admin/user_detail.html',
                         user=user,
                         recent_attendance=recent_attendance,
                         leave_requests=leave_requests)

@admin_bp.route('/users/<int:user_id>/toggle_status')
@login_required
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'error')
    else:
        user.is_active = not user.is_active
        db.session.commit()
        
        status = 'activated' if user.is_active else 'deactivated'
        flash(f'User {user.full_name} has been {status}.', 'success')
    
    return redirect(url_for('admin.user_detail', user_id=user_id))

@admin_bp.route('/departments')
@login_required
@admin_required
def departments():
    """Department management"""
    departments = Department.query.order_by(Department.name).all()
    
    # Get employee count for each department
    dept_stats = {}
    for dept in departments:
        dept_stats[dept.id] = User.query.filter_by(
            department_id=dept.id,
            is_active=True
        ).count()
    
    return render_template('admin/departments.html',
                         departments=departments,
                         dept_stats=dept_stats)

@admin_bp.route('/departments/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_department():
    """Create new department"""
    form = DepartmentForm()
    
    if form.validate_on_submit():
        department = Department(
            name=form.name.data,
            code=form.code.data.upper(),
            description=form.description.data,
            budget=float(form.budget.data) if form.budget.data else None
        )
        
        db.session.add(department)
        db.session.commit()
        
        flash(f'Department {department.name} created successfully!', 'success')
        return redirect(url_for('admin.departments'))
    
    return render_template('admin/department_form.html', form=form, title='New Department')

@admin_bp.route('/departments/<int:dept_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_department(dept_id):
    """Edit department"""
    department = Department.query.get_or_404(dept_id)
    form = DepartmentForm(obj=department, original_name=department.name, original_code=department.code)
    
    if form.validate_on_submit():
        department.name = form.name.data
        department.code = form.code.data.upper()
        department.description = form.description.data
        department.budget = float(form.budget.data) if form.budget.data else None
        
        db.session.commit()
        
        flash(f'Department {department.name} updated successfully!', 'success')
        return redirect(url_for('admin.departments'))
    
    return render_template('admin/department_form.html',
                         form=form,
                         department=department,
                         title='Edit Department')

@admin_bp.route('/attendance')
@login_required
@admin_required
def attendance():
    """System-wide attendance management"""
    page = request.args.get('page', 1, type=int)
    date_filter = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    department_filter = request.args.get('department', '', type=str)
    
    query = db.session.query(Attendance).join(User)
    
    if date_filter:
        filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
        query = query.filter(Attendance.date == filter_date)
    
    if department_filter:
        query = query.filter(User.department_id == department_filter)
    
    attendance_records = query.order_by(desc(Attendance.date), User.first_name).paginate(
        page=page, per_page=50, error_out=False
    )
    
    departments = Department.query.filter_by(is_active=True).all()
    
    # Daily statistics
    if date_filter:
        daily_stats = db.session.query(
            func.count(Attendance.id).label('total'),
            func.sum(func.case((Attendance.status == 'present', 1), else_=0)).label('present'),
            func.sum(func.case((Attendance.status == 'late', 1), else_=0)).label('late'),
            func.sum(func.case((Attendance.status == 'absent', 1), else_=0)).label('absent')
        ).filter(Attendance.date == filter_date).first()
    else:
        daily_stats = None
    
    return render_template('admin/attendance.html',
                         attendance_records=attendance_records,
                         departments=departments,
                         date_filter=date_filter,
                         department_filter=department_filter,
                         daily_stats=daily_stats)

@admin_bp.route('/leave_requests')
@login_required
@admin_required
def leave_requests():
    """Leave request management"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '', type=str)
    
    query = LeaveRequest.query.join(User)
    
    if status_filter:
        query = query.filter(LeaveRequest.status == status_filter)
    
    leave_requests = query.order_by(desc(LeaveRequest.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/leave_requests.html',
                         leave_requests=leave_requests,
                         status_filter=status_filter)

@admin_bp.route('/leave_requests/<int:request_id>/approve')
@login_required
@admin_required
def approve_leave_request(request_id):
    """Approve leave request"""
    leave_request = LeaveRequest.query.get_or_404(request_id)
    
    leave_request.status = 'approved'
    leave_request.approved_by = current_user.id
    leave_request.approved_at = datetime.utcnow()
    
    # Update leave balance
    if leave_request.leave_type == 'annual' and leave_request.user.employee_profile:
        leave_request.user.employee_profile.annual_leave_balance -= leave_request.days_requested
    elif leave_request.leave_type == 'sick' and leave_request.user.employee_profile:
        leave_request.user.employee_profile.sick_leave_balance -= leave_request.days_requested
    
    db.session.commit()
    
    flash(f'Leave request for {leave_request.user.full_name} has been approved.', 'success')
    return redirect(url_for('admin.leave_requests'))

@admin_bp.route('/leave_requests/<int:request_id>/reject')
@login_required
@admin_required
def reject_leave_request(request_id):
    """Reject leave request"""
    leave_request = LeaveRequest.query.get_or_404(request_id)
    
    leave_request.status = 'rejected'
    leave_request.approved_by = current_user.id
    leave_request.approved_at = datetime.utcnow()
    
    db.session.commit()
    
    flash(f'Leave request for {leave_request.user.full_name} has been rejected.', 'success')
    return redirect(url_for('admin.leave_requests'))

@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    """System reports"""
    return render_template('admin/reports.html')

@admin_bp.route('/settings')
@login_required
@admin_required
def settings():
    """System settings"""
    return render_template('admin/settings.html')
