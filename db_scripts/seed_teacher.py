#!/usr/bin/env python3
"""
Teacher seeding script - adds teacher accounts.
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

def seed_teachers():
    """Add teacher accounts to the database."""
    app = create_app()
    
    with app.app_context():
        print("👨‍🏫 Seeding teacher accounts...")
        
        teachers_data = [
            {
                'email': 'teacher1@test.com',
                'name': 'Dr. Sarah Johnson',
                'role': 'teacher'
            },
            {
                'email': 'teacher2@test.com', 
                'name': 'Prof. Michael Chen',
                'role': 'teacher'
            }
        ]
        
        created_count = 0
        
        for teacher_data in teachers_data:
            # Check if teacher already exists
            existing_teacher = User.query.filter_by(email=teacher_data['email']).first()
            if existing_teacher:
                print(f"   ⚠️  Teacher {teacher_data['email']} already exists, skipping...")
                continue
            
            # Create teacher
            teacher = User(
                email=teacher_data['email'],
                name=teacher_data['name'],
                role=teacher_data['role']
            )
            teacher.set_password('Sample12')
            
            db.session.add(teacher)
            created_count += 1
            print(f"   ✅ Created teacher: {teacher_data['name']} ({teacher_data['email']})")
        
        if created_count > 0:
            db.session.commit()
            print(f"\n✅ Successfully created {created_count} teacher(s)!")
        else:
            print("\n📝 No new teachers created (all already exist)")
        
        print("\n📋 Teacher Login Credentials:")
        print("   📧 teacher1@test.com | 🔑 Sample12")
        print("   📧 teacher2@test.com | 🔑 Sample12")

if __name__ == '__main__':
    try:
        seed_teachers()
    except Exception as e:
        print(f"❌ Error seeding teachers: {e}")
        sys.exit(1) 