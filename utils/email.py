from flask import current_app
from flask_mail import Message
from app import mail
import jwt
from datetime import datetime, timedelta

def send_password_reset_email(user):
    """Send password reset email to user"""
    token = generate_reset_token(user)
    
    msg = Message(
        subject='Password Reset Request - Mutech Civil HRM',
        recipients=[user.email],
        html=f"""
        <h2>Password Reset Request</h2>
        <p>Dear {user.first_name},</p>
        <p>You have requested to reset your password for the Mutech Civil HRM system.</p>
        <p>Click the link below to reset your password:</p>
        <p><a href="{current_app.config.get('BASE_URL', 'http://localhost:5000')}/auth/reset_password/{token}">Reset Password</a></p>
        <p>This link will expire in 1 hour.</p>
        <p>If you did not request this password reset, please ignore this email.</p>
        <p>Best regards,<br>Mutech Civil HRM System</p>
        """
    )
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def generate_reset_token(user):
    """Generate password reset token"""
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def verify_reset_token(token):
    """Verify password reset token"""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
        from models import User
        return User.query.get(user_id)
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
