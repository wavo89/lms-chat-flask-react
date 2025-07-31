#!/usr/bin/env python3
"""
Attendance seeding script - adds sample attendance records.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from datetime import date, timedelta
from flask import Flask
from config import Config
from models import db, User, AttendanceRecord

def create_app():
    """Create Flask app instance for database operations."""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def seed_attendance():
    """Add sample attendance records to the database."""
    app = create_app()
    
    with app.app_context():
        print("📊 Seeding attendance records...")
        
        # Get all students and teachers
        students = User.query.filter_by(role='student').all()
        teachers = User.query.filter_by(role='teacher').all()
        
        if not students:
            print("   ⚠️  No students found. Run seed_students.py first!")
            return
            
        if not teachers:
            print("   ⚠️  No teachers found. Run seed_teachers.py first!")
            return
        
        # Use first teacher as default
        teacher = teachers[0]
        
        # Generate attendance for the last 7 days
        dates_to_seed = []
        for i in range(7):
            attendance_date = date.today() - timedelta(days=i)
            # Skip weekends (optional)
            if attendance_date.weekday() < 5:  # Monday = 0, Sunday = 6
                dates_to_seed.append(attendance_date)
        
        created_count = 0
        
        for attendance_date in dates_to_seed:
            print(f"   📅 Processing {attendance_date}...")
            
            for student in students:
                # Check if record already exists
                existing_record = AttendanceRecord.query.filter_by(
                    student_id=student.id,
                    date=attendance_date
                ).first()
                
                if existing_record:
                    continue
                
                # Generate realistic attendance pattern
                # 80% present, 10% absent, 5% tardy, 5% excused
                rand = random.random()
                if rand < 0.80:
                    status = 'present'
                elif rand < 0.90:
                    status = 'absent'
                elif rand < 0.95:
                    status = 'tardy'
                else:
                    status = 'excused'
                
                # Create attendance record
                record = AttendanceRecord(
                    date=attendance_date,
                    status=status,
                    student_id=student.id,
                    teacher_id=teacher.id
                )
                
                db.session.add(record)
                created_count += 1
        
        if created_count > 0:
            db.session.commit()
            print(f"\n✅ Successfully created {created_count} attendance records!")
        else:
            print("\n📝 No new attendance records created (all already exist)")
        
        # Show summary
        print("\n📋 Attendance Summary:")
        for attendance_date in dates_to_seed[:3]:  # Show last 3 days
            records = AttendanceRecord.query.filter_by(date=attendance_date).all()
            status_counts = {}
            for record in records:
                status_counts[record.status] = status_counts.get(record.status, 0) + 1
            
            print(f"   {attendance_date}: {dict(status_counts)}")
        
        print(f"\n💡 Tip: Login as teacher1@test.com to view attendance records!")

if __name__ == '__main__':
    try:
        seed_attendance()
    except Exception as e:
        print(f"❌ Error seeding attendance: {e}")
        sys.exit(1) 