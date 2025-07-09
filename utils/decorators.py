from functools import wraps
from flask import abort, flash, redirect, url_for, request
from flask_login import current_user

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.url))
        
        if not current_user.has_role('admin'):
            flash('Access denied. Administrator privileges required.', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def permission_required(permission_name):
    """Decorator to require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login', next=request.url))
            
            if not current_user.has_permission(permission_name):
                flash(f'Access denied. {permission_name} permission required.', 'error')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def role_required(role_name):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login', next=request.url))
            
            if not current_user.has_role(role_name):
                flash(f'Access denied. {role_name} role required.', 'error')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def department_access_required(department_name=None):
    """Decorator to require access to specific department or user's own department"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login', next=request.url))
            
            # Admin can access all departments
            if current_user.has_role('admin'):
                return f(*args, **kwargs)
            
            # Check if user has access to the specified department
            if department_name:
                if current_user.department.name != department_name:
                    flash(f'Access denied. You do not have access to {department_name} department.', 'error')
                    abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def manager_required(f):
    """Decorator to require manager role or admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.url))
        
        if not (current_user.has_role('admin') or current_user.has_role('manager')):
            flash('Access denied. Manager privileges required.', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def own_profile_or_admin_required(f):
    """Decorator to allow access to own profile or admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.url))
        
        # Get user_id from URL parameters
        user_id = kwargs.get('user_id') or request.view_args.get('user_id')
        
        # Admin can access any profile
        if current_user.has_role('admin'):
            return f(*args, **kwargs)
        
        # User can access their own profile
        if user_id and int(user_id) == current_user.id:
            return f(*args, **kwargs)
        
        flash('Access denied. You can only access your own profile.', 'error')
        abort(403)
    
    return decorated_function

def active_user_required(f):
    """Decorator to ensure user account is active"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.url))
        
        if not current_user.is_active:
            flash('Your account has been deactivated. Please contact administrator.', 'error')
            return redirect(url_for('auth.logout'))
        
        return f(*args, **kwargs)
    return decorated_function
