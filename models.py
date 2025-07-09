from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from app import db

# Association tables for many-to-many relationships
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    """User model for authentication and profile management"""
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Personal Information
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    date_of_birth = db.Column(db.Date)
    national_id = db.Column(db.String(20), unique=True)
    
    # Employment Information
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    position = db.Column(db.String(100))
    hire_date = db.Column(db.Date, default=date.today)
    salary = db.Column(db.Decimal(10, 2))
    is_active = db.Column(db.Boolean, default=True)
    
    # System Information
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    department = db.relationship('Department', backref='employees')
    roles = db.relationship('Role', secondary=user_roles, backref='users')
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def has_permission(self, permission_name):
        """Check if user has specific permission"""
        for role in self.roles:
            for permission in role.permissions:
                if permission.name == permission_name:
                    return True
        return False
    
    def has_role(self, role_name):
        """Check if user has specific role"""
        return any(role.name == role_name for role in self.roles)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @staticmethod
    def verify_reset_password_token(token):
        """Verify password reset token"""
        from utils.email import verify_reset_token
        return verify_reset_token(token)

    def __repr__(self):
        return f'<User {self.email}>'

class Department(db.Model):
    """Department model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    description = db.Column(db.Text)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    budget = db.Column(db.Decimal(12, 2))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    manager = db.relationship('User', foreign_keys=[manager_id], post_update=True)
    
    def __repr__(self):
        return f'<Department {self.name}>'

class Role(db.Model):
    """Role model for access control"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    permissions = db.relationship('Permission', secondary=role_permissions, backref='roles')
    
    def __repr__(self):
        return f'<Role {self.name}>'

class Permission(db.Model):
    """Permission model for granular access control"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    resource = db.Column(db.String(50))  # e.g., 'users', 'departments', 'reports'
    action = db.Column(db.String(20))    # e.g., 'create', 'read', 'update', 'delete'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Permission {self.name}>'

class Employee(db.Model):
    """Extended employee information"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    
    # Emergency Contact
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    emergency_contact_relationship = db.Column(db.String(50))
    
    # Bank Information
    bank_name = db.Column(db.String(100))
    bank_account_number = db.Column(db.String(50))
    bank_branch = db.Column(db.String(100))
    
    # Leave Information
    annual_leave_balance = db.Column(db.Integer, default=21)
    sick_leave_balance = db.Column(db.Integer, default=10)
    
    # Performance
    performance_rating = db.Column(db.String(20))
    last_review_date = db.Column(db.Date)
    next_review_date = db.Column(db.Date)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('employee_profile', uselist=False))
    
    def __repr__(self):
        return f'<Employee {self.user.full_name}>'

class Attendance(db.Model):
    """Employee attendance tracking"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    check_in = db.Column(db.Time)
    check_out = db.Column(db.Time)
    break_start = db.Column(db.Time)
    break_end = db.Column(db.Time)
    status = db.Column(db.String(20), default='present')  # present, absent, late, half_day
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='attendance_records')
    
    @property
    def hours_worked(self):
        """Calculate hours worked"""
        if self.check_in and self.check_out:
            # Convert to datetime for calculation
            check_in_dt = datetime.combine(self.date, self.check_in)
            check_out_dt = datetime.combine(self.date, self.check_out)
            
            # Calculate break time
            break_time = 0
            if self.break_start and self.break_end:
                break_start_dt = datetime.combine(self.date, self.break_start)
                break_end_dt = datetime.combine(self.date, self.break_end)
                break_time = (break_end_dt - break_start_dt).total_seconds() / 3600
            
            total_hours = (check_out_dt - check_in_dt).total_seconds() / 3600
            return max(0, total_hours - break_time)
        return 0
    
    def __repr__(self):
        return f'<Attendance {self.user.full_name} - {self.date}>'

class LeaveRequest(db.Model):
    """Employee leave requests"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    leave_type = db.Column(db.String(50), nullable=False)  # annual, sick, maternity, etc.
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    days_requested = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_at = db.Column(db.DateTime)
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='leave_requests')
    approver = db.relationship('User', foreign_keys=[approved_by])

    def __repr__(self):
        return f'<LeaveRequest {self.user.full_name} - {self.leave_type}>'

class Payment(db.Model):
    """Payment records for MPESA and other transactions"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    payment_type = db.Column(db.String(50), nullable=False)  # salary, bonus, reimbursement, etc.
    amount = db.Column(db.Decimal(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='KES')

    # Payment method details
    payment_method = db.Column(db.String(20), nullable=False)  # mpesa, bank, cash
    phone_number = db.Column(db.String(20))  # For MPESA payments
    bank_account = db.Column(db.String(50))  # For bank transfers

    # MPESA specific fields
    mpesa_receipt_number = db.Column(db.String(50))
    checkout_request_id = db.Column(db.String(100))
    merchant_request_id = db.Column(db.String(100))

    # Payment status
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed, cancelled
    transaction_date = db.Column(db.DateTime)

    # Additional information
    description = db.Column(db.Text)
    reference_number = db.Column(db.String(50))
    processed_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='payments')
    processor = db.relationship('User', foreign_keys=[processed_by])

    def __repr__(self):
        return f'<Payment {self.user.full_name} - {self.amount} {self.currency}>'

class Payroll(db.Model):
    """Monthly payroll records"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)  # 1-12
    year = db.Column(db.Integer, nullable=False)

    # Salary components
    basic_salary = db.Column(db.Decimal(10, 2), nullable=False)
    allowances = db.Column(db.Decimal(10, 2), default=0)
    overtime_hours = db.Column(db.Decimal(5, 2), default=0)
    overtime_rate = db.Column(db.Decimal(8, 2), default=0)
    overtime_pay = db.Column(db.Decimal(10, 2), default=0)

    # Deductions
    tax_deduction = db.Column(db.Decimal(10, 2), default=0)
    nhif_deduction = db.Column(db.Decimal(10, 2), default=0)
    nssf_deduction = db.Column(db.Decimal(10, 2), default=0)
    other_deductions = db.Column(db.Decimal(10, 2), default=0)

    # Totals
    gross_pay = db.Column(db.Decimal(10, 2), nullable=False)
    total_deductions = db.Column(db.Decimal(10, 2), nullable=False)
    net_pay = db.Column(db.Decimal(10, 2), nullable=False)

    # Payment information
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'))
    payment_status = db.Column(db.String(20), default='pending')
    payment_date = db.Column(db.Date)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='payroll_records')
    payment = db.relationship('Payment', backref='payroll_record')

    def calculate_totals(self):
        """Calculate gross pay, total deductions, and net pay"""
        self.overtime_pay = self.overtime_hours * self.overtime_rate
        self.gross_pay = self.basic_salary + self.allowances + self.overtime_pay
        self.total_deductions = (self.tax_deduction + self.nhif_deduction +
                               self.nssf_deduction + self.other_deductions)
        self.net_pay = self.gross_pay - self.total_deductions

    def __repr__(self):
        return f'<Payroll {self.user.full_name} - {self.month}/{self.year}>'
