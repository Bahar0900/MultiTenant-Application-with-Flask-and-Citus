from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Tenant, Note
from app.extensions import db
from datetime import datetime

bp = Blueprint('routes', __name__)

@bp.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    return render_template('login.html')

@bp.route('/login', methods=['GET', 'POST'])
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        # First find tenant via user email (assuming email unique per tenant)
        # Here we find any user with this email to get tenant_id
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Please check your login details and try again.')
            return redirect(url_for('routes.login'))
        
        # Now query the user again with tenant_id and email to avoid ambiguity
        # (This is more relevant if you want to be extra cautious)
        user = User.query.filter_by(email=email, tenant_id=user.tenant_id).first()

        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('routes.login'))

        login_user(user, remember=remember)
        return redirect(url_for('routes.dashboard'))

    return render_template('login.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        tenant_name = request.form.get('tenant_name')
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists')
            return redirect(url_for('routes.register'))
        
        # Create or get tenant
        tenant = Tenant.query.filter_by(name=tenant_name).first()
        if not tenant:
            tenant = Tenant(name=tenant_name)
            db.session.add(tenant)
            db.session.commit()
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password, method='sha256'),
            tenant_id=tenant.id
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('routes.login'))
    
    return render_template('register.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

@bp.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            note = Note(content=content, user_id=current_user.id)
            db.session.add(note)
            db.session.commit()
            flash('Note added successfully!')
    
    # Get all notes for the current user
    user_notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.created_at.desc()).all()
    return render_template('notes.html', notes=user_notes)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.home'))