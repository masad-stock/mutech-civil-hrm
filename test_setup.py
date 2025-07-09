#!/usr/bin/env python3
"""
Test script to verify the Mutech Civil HRM system setup
"""

import os
import sys
import unittest
from datetime import date

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestSystemSetup(unittest.TestCase):
    """Test system setup and basic functionality"""
    
    def setUp(self):
        """Set up test environment"""
        os.environ['FLASK_ENV'] = 'testing'
        os.environ['DATABASE_URL'] = 'sqlite:///test.db'
        
        from app import create_app, db
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        # Create tables
        db.create_all()
        
        # Initialize system data
        from utils.permissions import initialize_system
        initialize_system()
    
    def tearDown(self):
        """Clean up after tests"""
        from app import db
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
        # Remove test database file
        if os.path.exists('test.db'):
            os.remove('test.db')
    
    def test_app_creation(self):
        """Test that the app is created successfully"""
        self.assertIsNotNone(self.app)
        self.assertEqual(self.app.config['TESTING'], True)
    
    def test_database_models(self):
        """Test that database models are working"""
        from models import User, Department, Role, Permission
        
        # Test department creation
        dept = Department.query.filter_by(code='PROC').first()
        self.assertIsNotNone(dept)
        self.assertEqual(dept.name, 'Procurement')
        
        # Test role creation
        admin_role = Role.query.filter_by(name='admin').first()
        self.assertIsNotNone(admin_role)
        
        # Test permission creation
        user_create_perm = Permission.query.filter_by(name='users.create').first()
        self.assertIsNotNone(user_create_perm)
    
    def test_user_creation(self):
        """Test user creation and authentication"""
        from models import User, Department, db
        
        # Get a department
        dept = Department.query.filter_by(code='PROC').first()
        
        # Create a test user
        user = User(
            employee_id='TEST001',
            email='test@mutechcivil.com',
            first_name='Test',
            last_name='User',
            department_id=dept.id,
            position='Test Position'
        )
        user.set_password('testpassword')
        
        db.session.add(user)
        db.session.commit()
        
        # Test password verification
        self.assertTrue(user.check_password('testpassword'))
        self.assertFalse(user.check_password('wrongpassword'))
        
        # Test user properties
        self.assertEqual(user.full_name, 'Test User')
        self.assertEqual(user.department.name, 'Procurement')
    
    def test_role_permissions(self):
        """Test role and permission system"""
        from models import User, Department, Role, db
        
        # Get admin role
        admin_role = Role.query.filter_by(name='admin').first()
        dept = Department.query.filter_by(code='ACHR').first()
        
        # Create admin user
        admin_user = User(
            employee_id='ADMIN001',
            email='admin@mutechcivil.com',
            first_name='Admin',
            last_name='User',
            department_id=dept.id,
            position='Administrator'
        )
        admin_user.set_password('adminpass')
        admin_user.roles.append(admin_role)
        
        db.session.add(admin_user)
        db.session.commit()
        
        # Test role assignment
        self.assertTrue(admin_user.has_role('admin'))
        self.assertFalse(admin_user.has_role('employee'))
        
        # Test permissions
        self.assertTrue(admin_user.has_permission('users.create'))
        self.assertTrue(admin_user.has_permission('departments.read'))
    
    def test_routes_accessibility(self):
        """Test that main routes are accessible"""
        # Test main page
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Test login page
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
        
        # Test protected routes redirect to login
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        response = self.client.get('/admin/dashboard')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_login_functionality(self):
        """Test login functionality"""
        from models import User, Department, Role, db
        
        # Create test user
        dept = Department.query.filter_by(code='ACHR').first()
        admin_role = Role.query.filter_by(name='admin').first()
        
        user = User(
            employee_id='LOGIN001',
            email='login@mutechcivil.com',
            first_name='Login',
            last_name='Test',
            department_id=dept.id,
            position='Test User'
        )
        user.set_password('loginpass')
        user.roles.append(admin_role)
        
        db.session.add(user)
        db.session.commit()
        
        # Test login
        response = self.client.post('/auth/login', data={
            'email': 'login@mutechcivil.com',
            'password': 'loginpass',
            'csrf_token': 'test'  # In testing, CSRF is disabled
        }, follow_redirects=True)
        
        # Should redirect to admin dashboard for admin user
        self.assertEqual(response.status_code, 200)
    
    def test_mpesa_client_initialization(self):
        """Test MPESA client can be initialized"""
        try:
            from utils.mpesa import MPESAClient
            
            # Set test environment variables
            self.app.config['MPESA_CONSUMER_KEY'] = 'test_key'
            self.app.config['MPESA_CONSUMER_SECRET'] = 'test_secret'
            self.app.config['MPESA_SHORTCODE'] = '123456'
            self.app.config['MPESA_PASSKEY'] = 'test_passkey'
            
            with self.app.app_context():
                client = MPESAClient()
                self.assertIsNotNone(client)
                self.assertEqual(client.environment, 'sandbox')
        except ImportError:
            self.skipTest("MPESA client dependencies not available")

def run_tests():
    """Run all tests"""
    print("Running Mutech Civil HRM System Tests...")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestSystemSetup)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed! System setup is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
