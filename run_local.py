#!/usr/bin/env python3
"""
Local development server runner for Mutech Civil HRM System
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_development_environment():
    """Set up development environment variables"""
    # Set default development values if not provided
    if not os.environ.get('SECRET_KEY'):
        os.environ['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    
    if not os.environ.get('DATABASE_URL'):
        os.environ['DATABASE_URL'] = 'sqlite:///mutech_hrm_dev.db'
    
    if not os.environ.get('FLASK_ENV'):
        os.environ['FLASK_ENV'] = 'development'
    
    # Email settings for development (optional)
    if not os.environ.get('MAIL_SERVER'):
        os.environ['MAIL_SERVER'] = 'smtp.gmail.com'
        os.environ['MAIL_PORT'] = '587'
    
    # MPESA settings for development (sandbox)
    if not os.environ.get('MPESA_ENVIRONMENT'):
        os.environ['MPESA_ENVIRONMENT'] = 'sandbox'

def initialize_database_if_needed():
    """Initialize database if it doesn't exist"""
    from app import create_app, db
    from models import User
    
    app = create_app()
    with app.app_context():
        # Check if database is initialized
        try:
            user_count = User.query.count()
            print(f"Database found with {user_count} users.")
        except Exception:
            print("Database not initialized. Running initialization...")
            
            # Import and run initialization
            from init_db import init_database
            init_database()
            
            print("Database initialized successfully!")

def main():
    """Main function to run the development server"""
    print("🏗️  Mutech Civil HRM System - Development Server")
    print("=" * 50)
    
    # Setup environment
    setup_development_environment()
    
    # Initialize database if needed
    try:
        initialize_database_if_needed()
    except Exception as e:
        print(f"Error initializing database: {e}")
        print("Please run 'python init_db.py' manually.")
        return
    
    # Import and create app
    from app import create_app
    app = create_app()
    
    # Get configuration
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🚀 Starting server at http://{host}:{port}")
    print(f"📊 Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"🗄️  Database: {os.environ.get('DATABASE_URL', 'Not set')}")
    print("=" * 50)
    print("📝 Default Admin Credentials:")
    print(f"   Email: {os.environ.get('ADMIN_EMAIL', 'admin@mutechcivil.com')}")
    print(f"   Password: {os.environ.get('ADMIN_PASSWORD', 'admin123')}")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        # Run the development server
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug,
            use_debugger=debug
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == '__main__':
    main()
