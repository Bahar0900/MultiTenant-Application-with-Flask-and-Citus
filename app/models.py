from datetime import datetime
from app.extensions import db, login_manager
from flask_login import UserMixin




@login_manager.user_loader
def load_user(user_id):
    try:
        id, tenant_id = map(int, user_id.split(":"))
        return db.session.get(User, (id, tenant_id))
    except Exception:
        return None
    
class Tenant(db.Model):
    __tablename__ = 'tenants'
    __table_args__ = {'schema': 'shared'}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'username', name='uix_tenant_username'),
        db.UniqueConstraint('tenant_id', 'email', name='uix_tenant_email'),
        {'schema': 'shared'}
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('shared.tenants.id'), primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    notes = db.relationship('Note', back_populates='user')

    def get_id(self):
        return f"{self.id}:{self.tenant_id}"

class Note(db.Model):
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('shared.users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='notes')

def configure_distributed_tables():
    # Create schema first
    db.session.execute('CREATE SCHEMA IF NOT EXISTS shared')
    db.session.commit()
    
    # Create reference table for tenants
    db.session.execute("""
    CREATE TABLE IF NOT EXISTS shared.tenants (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT NOW()
    )
    """)
    db.session.execute("SELECT create_reference_table('shared.tenants')")

    # Create users table
    db.session.execute("""
    CREATE TABLE IF NOT EXISTS shared.users (
        id SERIAL PRIMARY KEY,
        tenant_id INTEGER NOT NULL,
        username VARCHAR(50) NOT NULL,
        email VARCHAR(100) NOT NULL,
        password VARCHAR(100) NOT NULL,
        created_at TIMESTAMP DEFAULT NOW(),
        UNIQUE (tenant_id, username),
        UNIQUE (tenant_id, email)
    )
    """)
    db.session.execute("SELECT create_distributed_table('shared.users', 'tenant_id')")

    # Create notes table
    db.session.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id SERIAL PRIMARY KEY,
        content TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    )
    """)
    db.session.execute("SELECT create_distributed_table('notes', 'user_id', colocate_with => 'shared.users')")

    db.session.commit()
