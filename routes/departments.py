from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import User, Department, db
from utils.decorators import department_access_required, permission_required
from datetime import datetime, date

departments_bp = Blueprint('departments', __name__)

@departments_bp.route('/procurement')
@login_required
@department_access_required('Procurement')
def procurement():
    """Procurement department dashboard"""
    # Get department-specific data
    dept_employees = User.query.join(Department).filter(
        Department.name == 'Procurement',
        User.is_active == True
    ).all()
    
    # Procurement-specific metrics
    pending_requests = 0  # Placeholder for procurement requests
    approved_requests = 0
    total_budget = 0
    
    return render_template('departments/procurement.html',
                         dept_employees=dept_employees,
                         pending_requests=pending_requests,
                         approved_requests=approved_requests,
                         total_budget=total_budget)

@departments_bp.route('/accounts_hr')
@login_required
@department_access_required('Accounts/Human Resources')
def accounts_hr():
    """Accounts/HR department dashboard"""
    # Get all employees for HR overview
    if current_user.has_role('admin') or current_user.department.name == 'Accounts/Human Resources':
        all_employees = User.query.filter_by(is_active=True).all()
        total_employees = len(all_employees)
        
        # HR metrics
        new_hires_this_month = User.query.filter(
            User.hire_date >= date.today().replace(day=1),
            User.is_active == True
        ).count()
        
        # Payroll summary
        total_payroll = sum(emp.salary or 0 for emp in all_employees)
        
        return render_template('departments/accounts_hr.html',
                             all_employees=all_employees,
                             total_employees=total_employees,
                             new_hires_this_month=new_hires_this_month,
                             total_payroll=total_payroll)
    else:
        flash('Access denied to HR data.', 'error')
        return redirect(url_for('dashboard.index'))

@departments_bp.route('/spare_shop')
@login_required
@department_access_required('Spare Shop')
def spare_shop():
    """Spare Shop department dashboard"""
    dept_employees = User.query.join(Department).filter(
        Department.name == 'Spare Shop',
        User.is_active == True
    ).all()
    
    # Inventory metrics (placeholder)
    total_items = 0
    low_stock_items = 0
    pending_orders = 0
    
    return render_template('departments/spare_shop.html',
                         dept_employees=dept_employees,
                         total_items=total_items,
                         low_stock_items=low_stock_items,
                         pending_orders=pending_orders)

@departments_bp.route('/engineering')
@login_required
@department_access_required('Engineering Mechanical')
def engineering():
    """Engineering Mechanical department dashboard"""
    dept_employees = User.query.join(Department).filter(
        Department.name == 'Engineering Mechanical',
        User.is_active == True
    ).all()
    
    # Engineering metrics (placeholder)
    active_projects = 0
    pending_maintenance = 0
    equipment_count = 0
    
    return render_template('departments/engineering.html',
                         dept_employees=dept_employees,
                         active_projects=active_projects,
                         pending_maintenance=pending_maintenance,
                         equipment_count=equipment_count)

@departments_bp.route('/rentals')
@login_required
@department_access_required('Rentals')
def rentals():
    """Rentals department dashboard"""
    dept_employees = User.query.join(Department).filter(
        Department.name == 'Rentals',
        User.is_active == True
    ).all()
    
    # Rental metrics (placeholder)
    active_rentals = 0
    pending_returns = 0
    monthly_revenue = 0
    
    return render_template('departments/rentals.html',
                         dept_employees=dept_employees,
                         active_rentals=active_rentals,
                         pending_returns=pending_returns,
                         monthly_revenue=monthly_revenue)

@departments_bp.route('/financial')
@login_required
@department_access_required('Financial Management')
def financial():
    """Financial Management department dashboard"""
    dept_employees = User.query.join(Department).filter(
        Department.name == 'Financial Management',
        User.is_active == True
    ).all()
    
    # Financial metrics (placeholder)
    monthly_revenue = 0
    monthly_expenses = 0
    profit_margin = 0
    pending_approvals = 0
    
    return render_template('departments/financial.html',
                         dept_employees=dept_employees,
                         monthly_revenue=monthly_revenue,
                         monthly_expenses=monthly_expenses,
                         profit_margin=profit_margin,
                         pending_approvals=pending_approvals)

@departments_bp.route('/sales_marketing')
@login_required
@department_access_required('Sales & Marketing')
def sales_marketing():
    """Sales & Marketing department dashboard"""
    dept_employees = User.query.join(Department).filter(
        Department.name == 'Sales & Marketing',
        User.is_active == True
    ).all()
    
    # Sales metrics (placeholder)
    monthly_leads = 0
    converted_leads = 0
    active_campaigns = 0
    monthly_sales = 0
    
    return render_template('departments/sales_marketing.html',
                         dept_employees=dept_employees,
                         monthly_leads=monthly_leads,
                         converted_leads=converted_leads,
                         active_campaigns=active_campaigns,
                         monthly_sales=monthly_sales)

@departments_bp.route('/purchase_payables')
@login_required
@department_access_required('Purchase & Payables')
def purchase_payables():
    """Purchase & Payables department dashboard"""
    dept_employees = User.query.join(Department).filter(
        Department.name == 'Purchase & Payables',
        User.is_active == True
    ).all()
    
    # Purchase metrics (placeholder)
    pending_purchases = 0
    pending_payments = 0
    monthly_spend = 0
    vendor_count = 0
    
    return render_template('departments/purchase_payables.html',
                         dept_employees=dept_employees,
                         pending_purchases=pending_purchases,
                         pending_payments=pending_payments,
                         monthly_spend=monthly_spend,
                         vendor_count=vendor_count)

# Department-specific functionality routes

@departments_bp.route('/procurement/requests')
@login_required
@department_access_required('Procurement')
def procurement_requests():
    """Procurement requests management"""
    return render_template('departments/procurement_requests.html')

@departments_bp.route('/spare_shop/inventory')
@login_required
@department_access_required('Spare Shop')
def inventory_management():
    """Inventory management"""
    return render_template('departments/inventory.html')

@departments_bp.route('/engineering/projects')
@login_required
@department_access_required('Engineering Mechanical')
def engineering_projects():
    """Engineering projects management"""
    return render_template('departments/projects.html')

@departments_bp.route('/rentals/agreements')
@login_required
@department_access_required('Rentals')
def rental_agreements():
    """Rental agreements management"""
    return render_template('departments/rental_agreements.html')

@departments_bp.route('/sales_marketing/leads')
@login_required
@department_access_required('Sales & Marketing')
def sales_leads():
    """Sales leads management"""
    return render_template('departments/sales_leads.html')

@departments_bp.route('/financial/reports')
@login_required
@department_access_required('Financial Management')
def financial_reports():
    """Financial reports"""
    return render_template('departments/financial_reports.html')

@departments_bp.route('/purchase_payables/vendors')
@login_required
@department_access_required('Purchase & Payables')
def vendor_management():
    """Vendor management"""
    return render_template('departments/vendors.html')
