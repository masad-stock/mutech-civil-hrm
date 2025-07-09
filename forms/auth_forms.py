from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from models import User, Department

class LoginForm(FlaskForm):
    """Login form"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    """User registration form"""
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    department = QuerySelectField(
        'Department',
        validators=[DataRequired()],
        query_factory=lambda: Department.query.filter_by(is_active=True).all(),
        get_label='name'
    )
    position = StringField('Position', validators=[DataRequired(), Length(max=100)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register User')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('Email address already registered.')

class PasswordResetRequestForm(FlaskForm):
    """Password reset request form"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class PasswordResetForm(FlaskForm):
    """Password reset form"""
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')

class ChangePasswordForm(FlaskForm):
    """Change password form"""
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    new_password2 = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')

class ProfileForm(FlaskForm):
    """User profile form"""
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    address = TextAreaField('Address', validators=[Optional()])
    submit = SubmitField('Update Profile')

class DepartmentForm(FlaskForm):
    """Department form"""
    name = StringField('Department Name', validators=[DataRequired(), Length(min=2, max=100)])
    code = StringField('Department Code', validators=[DataRequired(), Length(min=2, max=10)])
    description = TextAreaField('Description', validators=[Optional()])
    budget = StringField('Budget', validators=[Optional()])
    submit = SubmitField('Save Department')
    
    def __init__(self, original_name=None, original_code=None, *args, **kwargs):
        super(DepartmentForm, self).__init__(*args, **kwargs)
        self.original_name = original_name
        self.original_code = original_code
    
    def validate_name(self, name):
        if name.data != self.original_name:
            department = Department.query.filter_by(name=name.data).first()
            if department:
                raise ValidationError('Department name already exists.')
    
    def validate_code(self, code):
        if code.data != self.original_code:
            department = Department.query.filter_by(code=code.data.upper()).first()
            if department:
                raise ValidationError('Department code already exists.')

class LeaveRequestForm(FlaskForm):
    """Leave request form"""
    leave_type = SelectField('Leave Type', validators=[DataRequired()], choices=[
        ('annual', 'Annual Leave'),
        ('sick', 'Sick Leave'),
        ('maternity', 'Maternity Leave'),
        ('paternity', 'Paternity Leave'),
        ('emergency', 'Emergency Leave'),
        ('unpaid', 'Unpaid Leave')
    ])
    start_date = StringField('Start Date', validators=[DataRequired()])
    end_date = StringField('End Date', validators=[DataRequired()])
    reason = TextAreaField('Reason', validators=[DataRequired()])
    submit = SubmitField('Submit Request')

class ChangePasswordForm(FlaskForm):
    """Change password form for logged-in users"""
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    new_password2 = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')
