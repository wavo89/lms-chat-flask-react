#!/usr/bin/env python3
"""
Attendance seeding script - adds sample attendance records with realistic patterns.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from datetime import date, timedelta
from flask import Flask
from config import Config
from models import db, User, AttendanceRecord, Class

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
        print("📋 Seeding attendance records...")
        
        # Clear existing attendance records first
        print("   🗑️  Clearing existing attendance records...")
        existing_records = AttendanceRecord.query.all()
        if existing_records:
            for record in existing_records:
                db.session.delete(record)
            db.session.commit()
            print(f"   ✅ Removed {len(existing_records)} existing attendance records")
        else:
            print("   ✅ No existing attendance records to remove")
        
        # Get all students and classes
        students = User.query.filter_by(role='student').all()
        if not students:
            print("   ⚠️  No students found. Please run seed_student.py first.")
            return
        
        classes = Class.query.filter_by(is_active=True).all()
        if not classes:
            print("   ⚠️  No classes found. Please run seed_classes.py first.")
            return
        
        # Get first teacher for attendance records
        teacher = User.query.filter_by(role='teacher').first()
        if not teacher:
            print("   ⚠️  No teachers found. Please run seed_teacher.py first.")
            return
        
        # Generate attendance for current date plus 4 previous weekdays (5 total)
        attendance_dates = []
        current_date = date.today()
        
        # Add 4 previous weekdays first
        weekdays_added = 0
        date_offset = 1
        
        while weekdays_added < 4:
            check_date = current_date - timedelta(days=date_offset)
            if check_date.weekday() < 5:  # Monday=0, Sunday=6
                attendance_dates.append(check_date)
                weekdays_added += 1
            date_offset += 1
        
        # Reverse to get chronological order (oldest first)
        attendance_dates.reverse()
        
        # Add current date at the end (most recent)
        attendance_dates.append(current_date)
        
        # Define student patterns for realistic attendance with more diversity
        # Some students have consistent patterns
        frequent_absentees = random.sample(students, min(6, len(students)))  # 6 students who are often absent (increased)
        chronic_tardies = random.sample([s for s in students if s not in frequent_absentees], min(4, len(students)-6))  # 4 students often tardy (increased)
        perfect_attendance = random.sample([s for s in students if s not in frequent_absentees and s not in chronic_tardies], min(3, len(students)-10))  # 3 perfect attendance (decreased)
        occasional_issues = [s for s in students if s not in frequent_absentees and s not in chronic_tardies and s not in perfect_attendance]  # Rest have occasional issues
        
        created_count = 0
        
        for i, attendance_date in enumerate(attendance_dates):
            print(f"   📅 Creating attendance for {attendance_date}")
            
            # Create attendance records for each class
            for class_obj in classes:
                print(f"      📚 Processing {class_obj.name} class...")
                
                for student in class_obj.students:
                    # Determine status based on student patterns and some randomness
                    if student in perfect_attendance:
                        # Perfect attendance students - always present
                        status = 'present'
                    else:
                        # Set up weights for other student types
                        if student in frequent_absentees:
                            # Frequent absentees - more absences and excused absences
                            # 45% absent, 25% excused, 25% present, 5% tardy
                            weights = [('absent', 45), ('excused', 25), ('present', 25), ('tardy', 5)]
                        elif student in chronic_tardies:
                            # Chronic tardies - often late but shows up
                            # 35% tardy, 55% present, 7% absent, 3% excused
                            weights = [('tardy', 35), ('present', 55), ('absent', 7), ('excused', 3)]
                        elif student in occasional_issues:
                            # Students with occasional issues - more varied attendance
                            # 70% present, 15% absent, 10% tardy, 5% excused
                            weights = [('present', 70), ('absent', 15), ('tardy', 10), ('excused', 5)]
                        else:
                            # Default fallback - mostly present
                            # 80% present, 10% absent, 6% tardy, 4% excused
                            weights = [('present', 80), ('absent', 10), ('tardy', 6), ('excused', 4)]
                        
                        # Add some day-of-week patterns for more realism
                        weekday = attendance_date.weekday()
                        if weekday == 0:  # Monday - more tardies and absences (weekend recovery)
                            weights = [(s, wt+3 if s == 'tardy' else wt+2 if s == 'absent' else wt-2 if s == 'present' else wt) for s, wt in weights]
                        elif weekday == 4:  # Friday - more absences and excused (long weekend starts)
                            weights = [(s, wt+4 if s == 'absent' else wt+2 if s == 'excused' else wt-2 if s == 'present' else wt) for s, wt in weights]
                        elif weekday == 2:  # Wednesday - generally better attendance (mid-week)
                            weights = [(s, wt+3 if s == 'present' else wt-1 if s != 'present' else wt) for s, wt in weights]
                        
                        # Create weighted list
                        weighted_statuses = []
                        for status_name, weight in weights:
                            weighted_statuses.extend([status_name] * max(1, weight))
                        
                        status = random.choice(weighted_statuses)
                    
                    # Add some consistency patterns for more realism
                    if i > 0:
                        yesterday = attendance_dates[i-1]
                        yesterday_record = AttendanceRecord.query.filter_by(
                            student_id=student.id,
                            date=yesterday,
                            class_id=class_obj.id
                        ).first()
                        
                        if yesterday_record:
                            # If absent yesterday, 35% chance to continue being absent (illness/issues)
                            if yesterday_record.status == 'absent' and random.random() < 0.35:
                                status = 'absent'
                            # If tardy yesterday, 25% chance to be tardy again (transportation issues)
                            elif yesterday_record.status == 'tardy' and random.random() < 0.25:
                                status = 'tardy'
                            # If excused yesterday, 20% chance to be excused again (family trips, medical)
                            elif yesterday_record.status == 'excused' and random.random() < 0.20:
                                status = 'excused'
                    
                    # Create attendance record
                    record = AttendanceRecord(
                        date=attendance_date,
                        status=status,
                        student_id=student.id,
                        teacher_id=teacher.id,
                        class_id=class_obj.id
                    )
                    
                    db.session.add(record)
                    created_count += 1
        
        # Commit all records
        db.session.commit()
        
        # Calculate some statistics
        total_class_days = len(attendance_dates) * len(classes)
        
        print(f"   ✅ Created {created_count} attendance records for {len(attendance_dates)} days across {len(classes)} classes")
        print(f"   📊 Pattern summary:")
        print(f"      • Perfect attendance: {len(perfect_attendance)} students")
        print(f"      • Frequent absentees: {len(frequent_absentees)} students") 
        print(f"      • Chronic tardies: {len(chronic_tardies)} students")
        print(f"      • Occasional issues: {len(occasional_issues)} students")
        print(f"      • Total students: {len(students)} students")
        print("   📋 Attendance seeding completed successfully!")

def get_comment(percentage, assignment_type):
    """Generate realistic teacher comments based on performance."""
    if percentage >= 95:
        comments = [
            "Excellent work! You've mastered this concept.",
            "Outstanding effort and understanding.",
            "Perfect execution - keep up the great work!"
        ]
    elif percentage >= 85:
        comments = [
            "Great job! Minor areas for improvement noted.",
            "Strong understanding demonstrated.",
            "Well done - you're on the right track."
        ]
    elif percentage >= 75:
        comments = [
            "Good effort. Review the feedback for improvement.",
            "You're getting there - practice will help.",
            "Solid work with room for growth."
        ]
    elif percentage >= 65:
        comments = [
            "Please see me for additional help with this topic.",
            "You're struggling with some key concepts. Let's work together.",
            "Additional practice needed - don't hesitate to ask for help."
        ]
    else:
        comments = [
            "Please schedule a meeting to discuss your progress.",
            "This needs significant improvement. Let's create a plan.",
            "I'm concerned about your understanding. Please see me soon."
        ]
    
    return random.choice(comments)

if __name__ == '__main__':
    seed_attendance() 