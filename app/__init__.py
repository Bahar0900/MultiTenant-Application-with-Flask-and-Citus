from flask import Flask
from config import Config
from app.extensions import db, login_manager
from app.models import configure_distributed_tables

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'routes.login'

    with app.app_context():
        try:
            # 1. Create schema
            db.session.execute('CREATE SCHEMA IF NOT EXISTS shared')
            db.session.commit()
            
            # 2. Create tenants table (reference table)
            db.session.execute("""
            CREATE TABLE IF NOT EXISTS shared.tenants (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT NOW()
            )
            """)
            # Check if 'shared.tenants' is already distributed
            result = db.session.execute("""
                SELECT 1 FROM pg_dist_partition
                WHERE logicalrelid = 'shared.tenants'::regclass
            """).fetchone()
            if not result:
                db.session.execute("SELECT create_reference_table('shared.tenants')")
            
            # 3. Create users table
            db.session.execute("""
            CREATE TABLE IF NOT EXISTS shared.users (
                id SERIAL,
                tenant_id INTEGER NOT NULL,
                username VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL,
                password VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                PRIMARY KEY (id, tenant_id),
                UNIQUE (tenant_id, username),
                UNIQUE (tenant_id, email)
            )
            """)
            # Check if 'shared.users' is already distributed
            result = db.session.execute("""
                SELECT 1 FROM pg_dist_partition
                WHERE logicalrelid = 'shared.users'::regclass
            """).fetchone()
            if not result:
                db.session.execute("SELECT create_distributed_table('shared.users', 'tenant_id')")
            
            # 4. Create notes table without constraints first
            db.session.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id SERIAL,
                content TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
            """)
            # Check if 'notes' is already distributed
            result = db.session.execute("""
                SELECT 1 FROM pg_dist_partition
                WHERE logicalrelid = 'notes'::regclass
            """).fetchone()
            if not result:
                db.session.execute("""
                    SELECT create_distributed_table('notes', 'user_id', 
                        colocate_with => 'shared.users')
                """)
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Database initialization failed: {str(e)}")
            raise

    # Register blueprints
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app
