from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Landing page"""
    if current_user.is_authenticated:
        if current_user.has_role('admin'):
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('dashboard.index'))
    
    return render_template('main/index.html')

@main_bp.route('/about')
def about():
    """About Mutech Civil"""
    return render_template('main/about.html')

@main_bp.route('/contact')
def contact():
    """Contact information"""
    return render_template('main/contact.html')
