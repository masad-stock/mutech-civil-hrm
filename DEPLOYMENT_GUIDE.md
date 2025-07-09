# Mutech Civil HRM - Deployment Guide

This guide will help you deploy the Mutech Civil HRM system to Render.com with MPESA integration.

## Prerequisites

1. **GitHub Account**: Your code should be in a GitHub repository
2. **Render.com Account**: Sign up at [render.com](https://render.com)
3. **Gmail Account**: For email notifications (or other SMTP provider)
4. **MPESA Developer Account**: For payment integration
5. **Domain (Optional)**: For custom domain setup

## Step 1: Prepare Your Repository

1. **Fork or Clone** this repository to your GitHub account
2. **Update Configuration** in your repository:
   - Modify `render.yaml` if needed
   - Update `README.md` with your specific information
   - Ensure all files are committed and pushed

## Step 2: MPESA API Setup

### Safaricom Developer Portal Setup

1. **Register** at [developer.safaricom.co.ke](https://developer.safaricom.co.ke)
2. **Create an App** in the developer portal
3. **Get Credentials**:
   - Consumer Key
   - Consumer Secret
   - Business Shortcode
   - Passkey (for STK Push)

### Test Credentials (Sandbox)
For testing, you can use Safaricom's sandbox environment:
- Consumer Key: `your_sandbox_consumer_key`
- Consumer Secret: `your_sandbox_consumer_secret`
- Shortcode: `174379` (test shortcode)
- Passkey: `bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919`

## Step 3: Email Setup (Gmail)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. **Note the credentials**:
   - Email: your-email@gmail.com
   - App Password: generated-16-character-password

## Step 4: Deploy to Render.com

### Option A: Automatic Deployment (Recommended)

1. **Connect GitHub**:
   - Log in to Render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub account
   - Select your repository

2. **Configure Service**:
   - Render will detect the `render.yaml` file
   - Review the configuration
   - Click "Create Web Service"

3. **Set Environment Variables**:
   ```
   SECRET_KEY=your-secret-key-here
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   MAIL_DEFAULT_SENDER=your-email@gmail.com
   MPESA_CONSUMER_KEY=your-mpesa-consumer-key
   MPESA_CONSUMER_SECRET=your-mpesa-consumer-secret
   MPESA_SHORTCODE=your-business-shortcode
   MPESA_PASSKEY=your-mpesa-passkey
   MPESA_ENVIRONMENT=sandbox
   BASE_URL=https://your-app-name.onrender.com
   ```

### Option B: Manual Deployment

1. **Create PostgreSQL Database**:
   - In Render dashboard: New + → PostgreSQL
   - Name: `mutech-hrm-db`
   - Note the connection string

2. **Create Web Service**:
   - New + → Web Service
   - Connect repository
   - Configure:
     - Name: `mutech-hrm`
     - Environment: `Python`
     - Build Command: `pip install -r requirements.txt && python init_db.py`
     - Start Command: `gunicorn app:app`

3. **Set Environment Variables** (same as above, plus):
   ```
   DATABASE_URL=your-postgresql-connection-string
   ```

## Step 5: Configure MPESA Callbacks

1. **Update Callback URLs** in MPESA Developer Portal:
   - Validation URL: `https://your-app-name.onrender.com/payments/mpesa/callback`
   - Confirmation URL: `https://your-app-name.onrender.com/payments/mpesa/callback`
   - Result URL: `https://your-app-name.onrender.com/payments/mpesa/result`
   - Timeout URL: `https://your-app-name.onrender.com/payments/mpesa/timeout`

## Step 6: Initial Setup

1. **Access Your Application**:
   - URL: `https://your-app-name.onrender.com`
   - Wait for deployment to complete (5-10 minutes)

2. **Login as Admin**:
   - Email: `admin@mutechcivil.com`
   - Password: `admin123`
   - **Change password immediately!**

3. **Create Departments and Users**:
   - Go to Admin → Departments
   - Verify all departments are created
   - Go to Admin → Users
   - Create user accounts for your employees

## Step 7: Production Configuration

### Security Settings

1. **Change Default Passwords**:
   - Admin password
   - Database passwords
   - API keys

2. **Update Environment Variables**:
   ```
   FLASK_ENV=production
   MPESA_ENVIRONMENT=production
   ```

3. **Configure Custom Domain** (Optional):
   - In Render dashboard: Settings → Custom Domains
   - Add your domain
   - Update DNS records

### Email Configuration

1. **Test Email Functionality**:
   - Try password reset
   - Check leave request notifications
   - Verify system emails

2. **Configure Email Templates** (Optional):
   - Customize email templates in `utils/email.py`
   - Add company branding

## Step 8: MPESA Production Setup

### Go Live Checklist

1. **Complete MPESA Certification**:
   - Test all payment flows
   - Submit for Safaricom review
   - Get production credentials

2. **Update Production Settings**:
   ```
   MPESA_ENVIRONMENT=production
   MPESA_CONSUMER_KEY=production_key
   MPESA_CONSUMER_SECRET=production_secret
   MPESA_SHORTCODE=production_shortcode
   MPESA_PASSKEY=production_passkey
   ```

3. **Test Production Payments**:
   - Small test transactions
   - Verify callback handling
   - Check payment status updates

## Step 9: Monitoring and Maintenance

### Application Monitoring

1. **Set up Monitoring**:
   - Render provides basic monitoring
   - Set up alerts for downtime
   - Monitor database performance

2. **Log Management**:
   - Check application logs regularly
   - Monitor MPESA transaction logs
   - Set up error notifications

### Backup Strategy

1. **Database Backups**:
   - Render PostgreSQL includes automatic backups
   - Consider additional backup solutions
   - Test restore procedures

2. **Code Backups**:
   - Ensure code is in version control
   - Tag releases
   - Document deployment procedures

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Check DATABASE_URL format
   - Verify PostgreSQL service is running
   - Check connection limits

2. **MPESA Integration Issues**:
   - Verify callback URLs are accessible
   - Check MPESA credentials
   - Monitor MPESA API status

3. **Email Not Working**:
   - Verify Gmail app password
   - Check SMTP settings
   - Test with different email providers

### Support Resources

- **Render Documentation**: [render.com/docs](https://render.com/docs)
- **MPESA API Docs**: [developer.safaricom.co.ke](https://developer.safaricom.co.ke)
- **Flask Documentation**: [flask.palletsprojects.com](https://flask.palletsprojects.com)

## Security Best Practices

1. **Environment Variables**:
   - Never commit secrets to code
   - Use strong, unique passwords
   - Rotate credentials regularly

2. **Application Security**:
   - Keep dependencies updated
   - Monitor security advisories
   - Use HTTPS everywhere

3. **Database Security**:
   - Regular security updates
   - Monitor access logs
   - Use strong passwords

## Performance Optimization

1. **Database Optimization**:
   - Add indexes for frequently queried fields
   - Monitor slow queries
   - Consider connection pooling

2. **Application Performance**:
   - Enable caching where appropriate
   - Optimize database queries
   - Monitor response times

3. **Scaling Considerations**:
   - Monitor resource usage
   - Plan for user growth
   - Consider CDN for static assets

---

## Quick Start Commands

```bash
# Local development
python run_local.py

# Run tests
python test_setup.py

# Initialize database
python init_db.py

# Create sample users
python init_db.py --sample-users
```

For additional support, please refer to the main README.md file or contact the development team.
