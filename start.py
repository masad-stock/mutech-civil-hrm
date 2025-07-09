#!/usr/bin/env python3
"""
Production startup script for Mutech Civil HRM System
This script is used by Render.com and other production environments
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main function to start the production server"""
    from app import create_app
    
    # Create the Flask application
    app = create_app()
    
    # Get configuration from environment
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    
    # Run the application
    app.run(
        host=host,
        port=port,
        debug=False,
        use_reloader=False
    )

if __name__ == '__main__':
    main()
