#!/usr/bin/env python3
"""
Student seeding script - adds student accounts.
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

def seed_students():
    """Add student accounts to the database."""
    app = create_app()
    
    with app.app_context():
        print("👨‍🎓 Seeding student accounts...")
        
        students_data = [
            {'email': 'student1@test.com', 'name': 'Alice Johnson', 'student_id': 'STU001'},
            {'email': 'student2@test.com', 'name': 'Bob Smith', 'student_id': 'STU002'},
            {'email': 'student3@test.com', 'name': 'Charlie Brown', 'student_id': 'STU003'},
            {'email': 'student4@test.com', 'name': 'Diana Wilson', 'student_id': 'STU004'},
            {'email': 'student5@test.com', 'name': 'Ethan Davis', 'student_id': 'STU005'},
            {'email': 'student6@test.com', 'name': 'Fiona Garcia', 'student_id': 'STU006'},
            {'email': 'student7@test.com', 'name': 'George Miller', 'student_id': 'STU007'},
            {'email': 'student8@test.com', 'name': 'Hannah Lee', 'student_id': 'STU008'},
            {'email': 'student9@test.com', 'name': 'Ian Martinez', 'student_id': 'STU009'},
            {'email': 'student10@test.com', 'name': 'Julia Thompson', 'student_id': 'STU010'}
        ]
        
        created_count = 0
        
        for student_data in students_data:
            # Check if student already exists
            existing_student = User.query.filter_by(email=student_data['email']).first()
            if existing_student:
                print(f"   ⚠️  Student {student_data['email']} already exists, skipping...")
                continue
            
            # Create student
            student = User(
                email=student_data['email'],
                name=student_data['name'],
                role='student',
                student_id=student_data['student_id']
            )
            student.set_password('Sample12')
            
            db.session.add(student)
            created_count += 1
            print(f"   ✅ Created student: {student_data['name']} ({student_data['student_id']})")
        
        if created_count > 0:
            db.session.commit()
            print(f"\n✅ Successfully created {created_count} student(s)!")
        else:
            print("\n📝 No new students created (all already exist)")
        
        print("\n📋 Student Login Credentials (all use password: Sample12):")
        for i in range(1, 11):
            print(f"   📧 student{i}@test.com | 🆔 STU{i:03d}")

if __name__ == '__main__':
    try:
        seed_students()
    except Exception as e:
        print(f"❌ Error seeding students: {e}")
        sys.exit(1) 