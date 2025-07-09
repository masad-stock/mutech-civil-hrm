# Mutech Civil HRM - Quick Start Guide

Get the Mutech Civil HRM system up and running in minutes!

## 🚀 Local Development (5 minutes)

### Prerequisites
- Python 3.8+ installed
- Git installed

### Steps

1. **Clone and Setup**
   ```bash
   cd mutech_hrm
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your settings (optional for local testing)
   ```

3. **Initialize Database**
   ```bash
   python init_db.py
   # Optional: Add sample users
   python init_db.py --sample-users
   ```

4. **Start the Server**
   ```bash
   python run_local.py
   ```

5. **Access the System**
   - Open: http://localhost:5000
   - Login: admin@mutechcivil.com / admin123
   - **Change password immediately!**

## 🌐 Deploy to Render.com (10 minutes)

### Prerequisites
- GitHub account
- Render.com account (free)
- Gmail account for emails

### Steps

1. **Fork Repository**
   - Fork this repository to your GitHub account

2. **Create Render Service**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect the configuration

3. **Set Environment Variables**
   ```
   SECRET_KEY=your-secret-key-here
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-gmail-app-password
   MAIL_DEFAULT_SENDER=your-email@gmail.com
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment
   - Access your app at: https://your-app-name.onrender.com

## 📱 MPESA Setup (Optional)

### For Testing (Sandbox)
```
MPESA_CONSUMER_KEY=your_sandbox_key
MPESA_CONSUMER_SECRET=your_sandbox_secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919
MPESA_ENVIRONMENT=sandbox
```

### For Production
1. Register at [developer.safaricom.co.ke](https://developer.safaricom.co.ke)
2. Create an app and get production credentials
3. Update environment variables with production values

## 🔧 System Features

### Admin Features
- **User Management**: Create, edit, deactivate users
- **Department Management**: Organize employees by departments
- **Attendance Monitoring**: Track employee attendance
- **Leave Management**: Approve/reject leave requests
- **Payment Processing**: Handle MPESA payments and payroll
- **Reports & Analytics**: Generate system reports

### Employee Features
- **Digital Clock In/Out**: Track daily attendance
- **Leave Requests**: Submit and track leave applications
- **Profile Management**: Update personal information
- **Payment History**: View salary and payment records
- **Department Portal**: Access department-specific tools

### Department Portals
- **Procurement**: Purchase requests, vendor management
- **Accounts/HR**: Employee management, payroll processing
- **Spare Shop**: Inventory and parts management
- **Engineering**: Project and equipment management
- **Rentals**: Equipment rental agreements
- **Financial**: Financial planning and reporting
- **Sales & Marketing**: Lead and campaign management
- **Purchase & Payables**: Vendor payments and AP

## 🔐 Default Accounts

### Admin Account
- **Email**: admin@mutechcivil.com
- **Password**: admin123
- **Access**: Full system access

### Sample Users (if created)
- **john.doe@mutechcivil.com** / password123 (Procurement)
- **jane.smith@mutechcivil.com** / password123 (Engineering)
- **mike.johnson@mutechcivil.com** / password123 (HR Manager)
- **sarah.wilson@mutechcivil.com** / password123 (Sales Manager)

## 🛠️ Troubleshooting

### Common Issues

**Database Error**
```bash
# Reset database
rm mutech_hrm_dev.db
python init_db.py
```

**Import Errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

**Permission Errors**
- Login as admin
- Go to Admin → Users
- Check user roles and permissions

**Email Not Working**
- Verify Gmail app password
- Check SMTP settings in .env

### Getting Help

1. **Check Logs**: Look at console output for errors
2. **Run Tests**: `python test_setup.py`
3. **Documentation**: See README.md and DEPLOYMENT_GUIDE.md
4. **Support**: Contact system administrator

## 📊 Next Steps

### After Setup
1. **Change Default Passwords**: Update admin and user passwords
2. **Create Departments**: Add/modify departments as needed
3. **Add Users**: Create employee accounts
4. **Configure MPESA**: Set up payment integration
5. **Customize**: Modify templates and settings as needed

### Production Checklist
- [ ] Change all default passwords
- [ ] Set up proper email configuration
- [ ] Configure MPESA for production
- [ ] Set up monitoring and backups
- [ ] Train users on the system
- [ ] Test all critical workflows

## 🎯 Key URLs

### Local Development
- **Main App**: http://localhost:5000
- **Admin Panel**: http://localhost:5000/admin/dashboard
- **API Docs**: http://localhost:5000/api/docs (if implemented)

### Production
- **Main App**: https://your-app-name.onrender.com
- **Admin Panel**: https://your-app-name.onrender.com/admin/dashboard

---

**Need help?** Check the full documentation in README.md or contact support.

**Ready to deploy?** Follow the detailed DEPLOYMENT_GUIDE.md for production setup.
