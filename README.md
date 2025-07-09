# Mutech Civil - Human Resource Management System

A comprehensive HRM system built with Flask for Mutech Civil Engineering company, featuring department-specific portals, MPESA payment integration, and role-based access control.

## Features

### Core Functionality
- **User Authentication & Authorization**: Secure login with role-based access control
- **Employee Management**: Complete employee lifecycle management
- **Attendance Tracking**: Digital clock-in/out with comprehensive reporting
- **Leave Management**: Streamlined leave request and approval process
- **MPESA Integration**: Seamless salary payments and financial transactions
- **Department Portals**: Specialized interfaces for each department
- **Admin Dashboard**: Comprehensive system administration tools

### Department Portals
- **Procurement**: Purchase requests and vendor management
- **Accounts/Human Resources**: Employee management and payroll
- **Spare Shop**: Inventory and parts management
- **Engineering Mechanical**: Project and equipment management
- **Rentals**: Equipment rental agreements and billing
- **Financial Management**: Financial planning and reporting
- **Sales & Marketing**: Lead management and campaigns
- **Purchase & Payables**: Vendor payments and accounts payable

## Technology Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login, Flask-Mail
- **Frontend**: Bootstrap 5, Chart.js, Font Awesome
- **Database**: PostgreSQL (production), SQLite (development)
- **Payment**: MPESA API integration
- **Deployment**: Render.com

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL (for production)
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mutech_hrm
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. **Initialize Database**
   ```bash
   python init_db.py
   # Optional: Add sample users for testing
   python init_db.py --sample-users
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000`

## Environment Variables

### Required Variables
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=your-database-url
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

### MPESA Configuration
```env
MPESA_CONSUMER_KEY=your-mpesa-consumer-key
MPESA_CONSUMER_SECRET=your-mpesa-consumer-secret
MPESA_SHORTCODE=your-business-shortcode
MPESA_PASSKEY=your-mpesa-passkey
MPESA_ENVIRONMENT=sandbox  # or production
```

### Admin User Configuration
```env
ADMIN_EMAIL=admin@mutechcivil.com
ADMIN_PASSWORD=admin123
ADMIN_FIRST_NAME=System
ADMIN_LAST_NAME=Administrator
```

## Deployment to Render.com

### Automatic Deployment
1. Fork this repository
2. Connect your GitHub account to Render.com
3. Create a new Web Service from your forked repository
4. Render will automatically detect the `render.yaml` configuration
5. Set the required environment variables in Render dashboard
6. Deploy!

### Manual Deployment Steps
1. **Create PostgreSQL Database**
   - Go to Render.com dashboard
   - Create a new PostgreSQL database
   - Note the connection string

2. **Create Web Service**
   - Create a new Web Service
   - Connect your repository
   - Set build command: `pip install -r requirements.txt && python init_db.py`
   - Set start command: `gunicorn app:app`

3. **Configure Environment Variables**
   - Set all required environment variables
   - Use the PostgreSQL connection string for `DATABASE_URL`

4. **Deploy**
   - Trigger deployment
   - Monitor logs for any issues

## Default Login Credentials

After initialization, you can login with:
- **Email**: admin@mutechcivil.com
- **Password**: admin123

**Important**: Change the default password immediately after first login.

## User Roles and Permissions

### Admin
- Full system access
- User management
- System configuration
- All department access

### HR Manager
- Employee management
- Payroll processing
- Leave approval
- Attendance oversight

### Department Manager
- Department employee management
- Leave approval for department
- Department reports

### Employee
- Personal profile management
- Attendance tracking
- Leave requests
- View personal records

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout
- `POST /auth/register` - User registration (admin only)

### Dashboard
- `GET /dashboard/` - User dashboard
- `GET /dashboard/profile` - User profile
- `GET /dashboard/attendance` - User attendance records

### Admin
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/users` - User management
- `GET /admin/departments` - Department management

### Payments
- `GET /payments/` - Payment dashboard
- `POST /payments/new` - Create payment
- `POST /payments/mpesa/callback` - MPESA callback

## MPESA Integration

The system integrates with Safaricom's MPESA API for:
- Salary payments (B2C)
- Employee payment requests (STK Push)
- Payment status tracking
- Transaction reporting

### MPESA Setup
1. Register for MPESA API access
2. Obtain consumer key and secret
3. Configure shortcode and passkey
4. Set callback URLs in MPESA portal
5. Update environment variables

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Security Considerations

- All passwords are hashed using Werkzeug
- CSRF protection enabled
- Session security configured
- Role-based access control
- Input validation and sanitization
- Secure headers implemented

## Support

For support and questions:
- Email: support@mutechcivil.com
- Documentation: [Link to documentation]
- Issues: [GitHub Issues]

## License

This project is proprietary software developed for Mutech Civil Engineering.

## Changelog

### Version 1.0.0
- Initial release
- Core HRM functionality
- MPESA integration
- Department portals
- Admin dashboard
- Role-based access control
