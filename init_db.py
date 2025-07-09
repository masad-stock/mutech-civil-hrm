#!/usr/bin/env python3
"""
Database initialization script for Mutech Civil HRM System
"""

import os
import sys
from datetime import date
from decimal import Decimal

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import User, Department, Role, Permission, Employee
from utils.permissions import initialize_system
from werkzeug.security import generate_password_hash

def init_database():
    """Initialize the database with default data"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        print("Initializing system data...")
        initialize_system()
        
        print("Creating admin user...")
        create_admin_user()
        
        print("Database initialization completed successfully!")

def create_admin_user():
    """Create the default admin user"""
    # Check if admin user already exists
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@mutechcivil.com')
    existing_admin = User.query.filter_by(email=admin_email).first()
    
    if existing_admin:
        print(f"Admin user {admin_email} already exists.")
        return
    
    # Get admin role
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        print("Error: Admin role not found. Please run initialize_system() first.")
        return
    
    # Get Accounts/HR department (default for admin)
    hr_dept = Department.query.filter_by(code='ACHR').first()
    if not hr_dept:
        print("Error: Accounts/HR department not found.")
        return
    
    # Create admin user
    admin_user = User(
        employee_id='ADMIN001',
        email=admin_email,
        first_name=os.environ.get('ADMIN_FIRST_NAME', 'System'),
        last_name=os.environ.get('ADMIN_LAST_NAME', 'Administrator'),
        phone='+254700000000',
        department_id=hr_dept.id,
        position='System Administrator',
        hire_date=date.today(),
        salary=Decimal('100000.00'),
        is_active=True
    )
    
    # Set password
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
    admin_user.set_password(admin_password)
    
    # Add admin role
    admin_user.roles.append(admin_role)
    
    db.session.add(admin_user)
    db.session.flush()  # Get user ID
    
    # Create employee profile
    employee_profile = Employee(
        user_id=admin_user.id,
        emergency_contact_name='Emergency Contact',
        emergency_contact_phone='+254700000001',
        emergency_contact_relationship='Family',
        bank_name='KCB Bank',
        bank_account_number='1234567890',
        bank_branch='Nairobi Branch',
        annual_leave_balance=21,
        sick_leave_balance=10,
        performance_rating='Excellent'
    )
    
    db.session.add(employee_profile)
    db.session.commit()
    
    print(f"Admin user created successfully!")
    print(f"Email: {admin_email}")
    print(f"Password: {admin_password}")
    print("Please change the default password after first login.")

def create_sample_users():
    """Create sample users for testing (optional)"""
    app = create_app()
    
    with app.app_context():
        # Sample users data
        sample_users = [
            {
                'email': 'john.doe@mutechcivil.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'department_code': 'PROC',
                'position': 'Procurement Officer',
                'role': 'procurement_officer'
            },
            {
                'email': 'jane.smith@mutechcivil.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'department_code': 'ENGM',
                'position': 'Senior Engineer',
                'role': 'engineer'
            },
            {
                'email': 'mike.johnson@mutechcivil.com',
                'first_name': 'Mike',
                'last_name': 'Johnson',
                'department_code': 'ACHR',
                'position': 'HR Manager',
                'role': 'hr_manager'
            },
            {
                'email': 'sarah.wilson@mutechcivil.com',
                'first_name': 'Sarah',
                'last_name': 'Wilson',
                'department_code': 'SALM',
                'position': 'Sales Manager',
                'role': 'sales_manager'
            }
        ]
        
        for user_data in sample_users:
            # Check if user already exists
            existing_user = User.query.filter_by(email=user_data['email']).first()
            if existing_user:
                continue
            
            # Get department
            department = Department.query.filter_by(code=user_data['department_code']).first()
            if not department:
                continue
            
            # Get role
            role = Role.query.filter_by(name=user_data['role']).first()
            if not role:
                continue
            
            # Generate employee ID
            last_user = User.query.filter(
                User.employee_id.like(f'{department.code}%')
            ).order_by(User.employee_id.desc()).first()
            
            if last_user:
                try:
                    last_number = int(last_user.employee_id[len(department.code):])
                    new_number = last_number + 1
                except ValueError:
                    new_number = 1
            else:
                new_number = 1
            
            employee_id = f"{department.code}{new_number:04d}"
            
            # Create user
            user = User(
                employee_id=employee_id,
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                phone=f'+25470{new_number:07d}',
                department_id=department.id,
                position=user_data['position'],
                hire_date=date.today(),
                salary=Decimal('50000.00'),
                is_active=True
            )
            
            # Set default password
            user.set_password('password123')
            
            # Add role
            user.roles.append(role)
            
            db.session.add(user)
            
            print(f"Created sample user: {user.email}")
        
        db.session.commit()
        print("Sample users created successfully!")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize Mutech Civil HRM Database')
    parser.add_argument('--sample-users', action='store_true', 
                       help='Create sample users for testing')
    
    args = parser.parse_args()
    
    # Initialize database
    init_database()
    
    # Create sample users if requested
    if args.sample_users:
        create_sample_users()
    
    print("\nDatabase initialization completed!")
    print("You can now start the application with: python app.py")
