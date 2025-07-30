#!/usr/bin/env python3
"""
Admin seeding script - adds admin account.
"""

import sys
from flask import Flask
from config import Config
from models import db, User

def create_app():
    """Create Flask app instance for database operations."""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def seed_admin():
    """Add admin account to the database."""
    app = create_app()
    
    with app.app_context():
        print("👑 Seeding admin account...")
        
        # Check if admin user already exists
        existing_admin = User.query.filter_by(email='admin@test.com').first()
        if existing_admin:
            print("⚠️  Admin user already exists, skipping...")
            return
        
        # Create admin user
        admin_user = User(
            email='admin@test.com',
            name='Admin User',
            role='admin'
        )
        admin_user.set_password('Sample12')
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("✅ Admin seeded successfully!")
        print(f"   📧 Admin user: admin@test.com")
        print(f"   🔑 Password: Sample12")
        print(f"   👑 Role: admin")
        print(f"   🆔 User ID: {admin_user.id}")
        print("\n💡 Tip: Use seed_teachers.py and seed_students.py to add more users!")

if __name__ == '__main__':
    try:
        seed_admin()
    except Exception as e:
        print(f"❌ Error seeding admin: {e}")
        sys.exit(1) 