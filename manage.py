"""
Management CLI - Database operations and utilities
"""
import os
import sys
import click
from flask.cli import with_appcontext

from inventory_app import create_app
from inventory_app.extensions import db
from inventory_app.models.user import User

# Create application
app = create_app()


@click.command()
@with_appcontext
def init_db():
    """Initialize database tables"""
    db.create_all()
    click.echo('Database initialized successfully!')


@click.command()
@click.option('--username', prompt='Admin username', help='Admin username')
@click.option('--email', prompt='Admin email', help='Admin email')
@click.option('--password', prompt='Admin password', hide_input=True, help='Admin password')
@click.option('--first-name', prompt='First name (optional)', default='', help='First name')
@click.option('--last-name', prompt='Last name (optional)', default='', help='Last name')
@with_appcontext
def create_admin(username, email, password, first_name, last_name):
    """Create an admin user"""
    try:
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            click.echo(f'Error: User "{username}" already exists!')
            return
        
        if User.query.filter_by(email=email).first():
            click.echo(f'Error: Email "{email}" already exists!')
            return
        
        # Create admin user
        admin = User.create_admin_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name if first_name else None,
            last_name=last_name if last_name else None
        )
        
        db.session.add(admin)
        db.session.commit()
        
        click.echo(f'Admin user "{username}" created successfully!')
    except Exception as e:
        click.echo(f'Error creating admin user: {str(e)}')
        sys.exit(1)


@click.command()
@with_appcontext
def db_stats():
    """Show database statistics"""
    from inventory_app.models.equipment import Equipment
    
    user_count = User.query.count()
    active_users = User.query.filter_by(is_active=True, status='Aprovado').count()
    pending_users = User.query.filter_by(status='Pendente').count()
    equipment_count = Equipment.query.count()
    
    click.echo('=== Database Statistics ===')
    click.echo(f'Total Users: {user_count}')
    click.echo(f'Active Users: {active_users}')
    click.echo(f'Pending Approvals: {pending_users}')
    click.echo(f'Total Equipment: {equipment_count}')


@click.command()
@with_appcontext  
def check_db():
    """Check database connection"""
    try:
        # Try a simple query
        result = db.session.execute('SELECT 1').scalar()
        if result == 1:
            click.echo('✅ Database connection successful!')
            click.echo(f'Database URL: {app.config["SQLALCHEMY_DATABASE_URI"][:50]}...')
        else:
            click.echo('❌ Database connection failed!')
    except Exception as e:
        click.echo(f'❌ Database connection error: {str(e)}')


# Register CLI commands
app.cli.add_command(init_db)
app.cli.add_command(create_admin)
app.cli.add_command(db_stats)
app.cli.add_command(check_db)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)