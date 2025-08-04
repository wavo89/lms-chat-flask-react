#!/usr/bin/env python3
"""
Student seeding script - adds student accounts.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
        
        # Clear existing students first (need to handle attendance records)
        print("   🗑️  Clearing existing students...")
        existing_students = User.query.filter_by(role='student').all()
        student_count = len(existing_students)
        
        if student_count > 0:
            # First delete all attendance records for students
            from models import AttendanceRecord
            student_ids = [s.id for s in existing_students]
            attendance_records = AttendanceRecord.query.filter(AttendanceRecord.student_id.in_(student_ids)).all()
            for record in attendance_records:
                db.session.delete(record)
            
            # Then delete the students
            for student in existing_students:
                db.session.delete(student)
            
            db.session.commit()
            print(f"   ✅ Removed {len(attendance_records)} attendance records and {student_count} existing students")
        else:
            print("   ✅ No existing students to remove")
        
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
            {'email': 'student10@test.com', 'name': 'Julia Thompson', 'student_id': 'STU010'},
            {'email': 'student11@test.com', 'name': 'Kevin Rodriguez', 'student_id': 'STU011'},
            {'email': 'student12@test.com', 'name': 'Laura Anderson', 'student_id': 'STU012'},
            {'email': 'student13@test.com', 'name': 'Michael Chen', 'student_id': 'STU013'},
            {'email': 'student14@test.com', 'name': 'Nina Patel', 'student_id': 'STU014'},
            {'email': 'student15@test.com', 'name': 'Oliver Kim', 'student_id': 'STU015'},
            {'email': 'student16@test.com', 'name': 'Priya Singh', 'student_id': 'STU016'},
            {'email': 'student17@test.com', 'name': 'Quinn Taylor', 'student_id': 'STU017'},
            {'email': 'student18@test.com', 'name': 'Rachel Green', 'student_id': 'STU018'},
            {'email': 'student19@test.com', 'name': 'Samuel Jones', 'student_id': 'STU019'},
            {'email': 'student20@test.com', 'name': 'Tina White', 'student_id': 'STU020'},
            {'email': 'student21@test.com', 'name': 'Uma Patel', 'student_id': 'STU021'},
            {'email': 'student22@test.com', 'name': 'Victor Lopez', 'student_id': 'STU022'},
            {'email': 'student23@test.com', 'name': 'Wendy Clark', 'student_id': 'STU023'},
            {'email': 'student24@test.com', 'name': 'Xavier Young', 'student_id': 'STU024'},
            {'email': 'student25@test.com', 'name': 'Yasmin Ali', 'student_id': 'STU025'}
        ]
        
        created_count = 0
        
        for student_data in students_data:
            
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