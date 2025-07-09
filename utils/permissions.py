"""
Permission and role management utilities
"""

from models import Permission, Role, Department, db

# Define all permissions
PERMISSIONS = {
    # User management
    'users.create': 'Create new users',
    'users.read': 'View user information',
    'users.update': 'Update user information',
    'users.delete': 'Delete users',
    'users.manage_roles': 'Manage user roles',
    
    # Department management
    'departments.create': 'Create new departments',
    'departments.read': 'View department information',
    'departments.update': 'Update department information',
    'departments.delete': 'Delete departments',
    'departments.manage_budget': 'Manage department budgets',
    
    # Employee management
    'employees.create': 'Create employee profiles',
    'employees.read': 'View employee information',
    'employees.update': 'Update employee information',
    'employees.delete': 'Delete employee profiles',
    'employees.view_salary': 'View employee salaries',
    'employees.update_salary': 'Update employee salaries',
    
    # Attendance management
    'attendance.create': 'Record attendance',
    'attendance.read': 'View attendance records',
    'attendance.update': 'Update attendance records',
    'attendance.delete': 'Delete attendance records',
    'attendance.view_all': 'View all department attendance',
    
    # Leave management
    'leave.create': 'Submit leave requests',
    'leave.read': 'View leave requests',
    'leave.update': 'Update leave requests',
    'leave.delete': 'Delete leave requests',
    'leave.approve': 'Approve/reject leave requests',
    'leave.view_all': 'View all department leave requests',
    
    # Reports and analytics
    'reports.view': 'View reports',
    'reports.create': 'Create custom reports',
    'reports.export': 'Export reports',
    'reports.financial': 'View financial reports',
    
    # System administration
    'system.settings': 'Manage system settings',
    'system.backup': 'Perform system backups',
    'system.logs': 'View system logs',
    'system.maintenance': 'Perform system maintenance',
    
    # Payment management
    'payments.create': 'Process payments',
    'payments.read': 'View payment records',
    'payments.update': 'Update payment information',
    'payments.delete': 'Delete payment records',
    'payments.approve': 'Approve payments',
    'payments.mpesa': 'Manage MPESA transactions',
    
    # Procurement
    'procurement.create': 'Create procurement requests',
    'procurement.read': 'View procurement records',
    'procurement.update': 'Update procurement information',
    'procurement.approve': 'Approve procurement requests',
    
    # Inventory/Spare Shop
    'inventory.create': 'Add inventory items',
    'inventory.read': 'View inventory',
    'inventory.update': 'Update inventory',
    'inventory.delete': 'Remove inventory items',
    'inventory.transfer': 'Transfer inventory items',
    
    # Engineering
    'engineering.projects': 'Manage engineering projects',
    'engineering.equipment': 'Manage equipment',
    'engineering.maintenance': 'Schedule maintenance',
    
    # Rentals
    'rentals.create': 'Create rental agreements',
    'rentals.read': 'View rental information',
    'rentals.update': 'Update rental agreements',
    'rentals.billing': 'Manage rental billing',
    
    # Sales & Marketing
    'sales.leads': 'Manage sales leads',
    'sales.quotes': 'Create quotes',
    'sales.contracts': 'Manage contracts',
    'marketing.campaigns': 'Manage marketing campaigns',
}

# Define roles and their permissions
ROLES = {
    'admin': {
        'description': 'System Administrator with full access',
        'permissions': list(PERMISSIONS.keys())  # All permissions
    },
    'hr_manager': {
        'description': 'Human Resources Manager',
        'permissions': [
            'users.create', 'users.read', 'users.update', 'users.manage_roles',
            'employees.create', 'employees.read', 'employees.update', 'employees.view_salary', 'employees.update_salary',
            'attendance.read', 'attendance.update', 'attendance.view_all',
            'leave.read', 'leave.approve', 'leave.view_all',
            'reports.view', 'reports.create', 'reports.export',
            'payments.read', 'payments.create'
        ]
    },
    'department_manager': {
        'description': 'Department Manager',
        'permissions': [
            'users.read', 'employees.read', 'employees.update',
            'attendance.read', 'attendance.update', 'attendance.view_all',
            'leave.read', 'leave.approve', 'leave.view_all',
            'reports.view', 'departments.read', 'departments.update'
        ]
    },
    'employee': {
        'description': 'Regular Employee',
        'permissions': [
            'attendance.create', 'attendance.read',
            'leave.create', 'leave.read',
            'employees.read'  # Own profile only
        ]
    },
    'procurement_officer': {
        'description': 'Procurement Officer',
        'permissions': [
            'procurement.create', 'procurement.read', 'procurement.update', 'procurement.approve',
            'inventory.read', 'reports.view', 'employees.read'
        ]
    },
    'accountant': {
        'description': 'Accountant',
        'permissions': [
            'payments.create', 'payments.read', 'payments.update', 'payments.approve', 'payments.mpesa',
            'reports.view', 'reports.financial', 'employees.read', 'employees.view_salary'
        ]
    },
    'inventory_manager': {
        'description': 'Inventory/Spare Shop Manager',
        'permissions': [
            'inventory.create', 'inventory.read', 'inventory.update', 'inventory.delete', 'inventory.transfer',
            'reports.view', 'employees.read'
        ]
    },
    'engineer': {
        'description': 'Engineering Staff',
        'permissions': [
            'engineering.projects', 'engineering.equipment', 'engineering.maintenance',
            'inventory.read', 'reports.view', 'employees.read'
        ]
    },
    'rental_manager': {
        'description': 'Rentals Manager',
        'permissions': [
            'rentals.create', 'rentals.read', 'rentals.update', 'rentals.billing',
            'payments.read', 'reports.view', 'employees.read'
        ]
    },
    'sales_manager': {
        'description': 'Sales & Marketing Manager',
        'permissions': [
            'sales.leads', 'sales.quotes', 'sales.contracts',
            'marketing.campaigns', 'reports.view', 'employees.read'
        ]
    }
}

def create_permissions():
    """Create all permissions in the database"""
    for name, description in PERMISSIONS.items():
        permission = Permission.query.filter_by(name=name).first()
        if not permission:
            # Extract resource and action from permission name
            parts = name.split('.')
            resource = parts[0] if len(parts) > 1 else 'general'
            action = parts[1] if len(parts) > 1 else name
            
            permission = Permission(
                name=name,
                description=description,
                resource=resource,
                action=action
            )
            db.session.add(permission)
    
    db.session.commit()
    print("Permissions created successfully!")

def create_roles():
    """Create all roles and assign permissions"""
    create_permissions()  # Ensure permissions exist first
    
    for role_name, role_data in ROLES.items():
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(
                name=role_name,
                description=role_data['description']
            )
            db.session.add(role)
            db.session.flush()  # Get the role ID
        
        # Clear existing permissions and add new ones
        role.permissions.clear()
        
        for permission_name in role_data['permissions']:
            permission = Permission.query.filter_by(name=permission_name).first()
            if permission:
                role.permissions.append(permission)
    
    db.session.commit()
    print("Roles created successfully!")

def create_departments():
    """Create default departments"""
    departments_data = [
        {'name': 'Procurement', 'code': 'PROC', 'description': 'Procurement and purchasing department'},
        {'name': 'Accounts/Human Resources', 'code': 'ACHR', 'description': 'Accounting and Human Resources department'},
        {'name': 'Spare Shop', 'code': 'SPAR', 'description': 'Spare parts and inventory management'},
        {'name': 'Engineering Mechanical', 'code': 'ENGM', 'description': 'Mechanical engineering department'},
        {'name': 'Rentals', 'code': 'RENT', 'description': 'Equipment rental management'},
        {'name': 'Financial Management', 'code': 'FINM', 'description': 'Financial management and planning'},
        {'name': 'Sales & Marketing', 'code': 'SALM', 'description': 'Sales and marketing department'},
        {'name': 'Purchase & Payables', 'code': 'PURC', 'description': 'Purchase and accounts payable'},
    ]
    
    for dept_data in departments_data:
        department = Department.query.filter_by(code=dept_data['code']).first()
        if not department:
            department = Department(
                name=dept_data['name'],
                code=dept_data['code'],
                description=dept_data['description']
            )
            db.session.add(department)
    
    db.session.commit()
    print("Departments created successfully!")

def initialize_system():
    """Initialize the system with default data"""
    create_departments()
    create_permissions()
    create_roles()
    print("System initialization completed!")
