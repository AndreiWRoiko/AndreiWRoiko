#!/usr/bin/env python3
"""Script to create admin user"""
from inventory_app import create_app
from inventory_app.models.user import User
from inventory_app.extensions import db

app = create_app()

with app.app_context():
    # Check if admin already exists
    existing_admin = User.query.filter_by(username='admin').first()
    if existing_admin:
        print('⚠️  Admin user already exists!')
        print(f'Username: {existing_admin.username}')
        print(f'Email: {existing_admin.email}')
        print(f'Role: {existing_admin.role}')
        print(f'Status: {existing_admin.status}')
    else:
        # Create admin user
        admin = User.create_admin_user(
            username='admin',
            email='admin@inventory.local',
            password='Admin123!',
            first_name='System',
            last_name='Admin'
        )
        db.session.add(admin)
        db.session.commit()
        print('✅ Admin user created successfully!')
        print('Username: admin')
        print('Password: Admin123!')
        print('Email: admin@inventory.local')
        print('Role: ADM (Administrator)')
        print('Status: Aprovado (Approved)')
