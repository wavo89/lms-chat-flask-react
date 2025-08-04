#!/usr/bin/env python3
"""
Classes seeding script - creates Math and ELA classes with ~80% overlapping students.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from flask import Flask
from config import Config
from models import db, User, Class

def create_app():
    """Create Flask app instance for database operations."""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def seed_classes():
    """Add Math and ELA classes to the database with overlapping students."""
    app = create_app()
    
    with app.app_context():
        print("📚 Seeding classes...")
        
        # Clear existing classes and enrollments first
        print("   🗑️  Clearing existing classes...")
        existing_classes = Class.query.all()
        if existing_classes:
            # Clear student enrollments first (many-to-many relationships)
            for class_obj in existing_classes:
                class_obj.students.clear()
            db.session.commit()
            
            # Then delete the classes
            for class_obj in existing_classes:
                db.session.delete(class_obj)
            db.session.commit()
            print(f"   ✅ Removed {len(existing_classes)} existing classes and their enrollments")
        else:
            print("   ✅ No existing classes to remove")
        
        # Get all students and teachers
        students = User.query.filter_by(role='student').all()
        teacher = User.query.filter_by(role='teacher').first()
        
        if not students:
            print("   ⚠️  No students found. Please run seed_student.py first.")
            return
        
        if not teacher:
            print("   ⚠️  No teachers found. Please run seed_teacher.py first.")
            return
        
        # Create Math class
        math_class = Class(
            name="Math",
            description="Mathematics class covering algebra, geometry, and problem solving",
            teacher_id=teacher.id
        )
        db.session.add(math_class)
        
        # Create ELA class
        ela_class = Class(
            name="ELA",
            description="English Language Arts class covering reading, writing, and literature",
            teacher_id=teacher.id
        )
        db.session.add(ela_class)
        
        # Commit to get IDs
        db.session.commit()
        
        # Enroll students with ~80% overlap
        print("   👥 Enrolling students in classes...")
        
        total_students = len(students)
        
        # Math class: enroll ~90% of students (to ensure good overlap)
        math_enrollment_count = max(1, int(total_students * 0.9))
        math_students = random.sample(students, math_enrollment_count)
        
        for student in math_students:
            math_class.students.append(student)
        
        # ELA class: start with ~80% of Math students for overlap, then add more to reach ~90% total
        overlap_count = max(1, int(len(math_students) * 0.8))
        ela_students_from_math = random.sample(math_students, overlap_count)
        
        # Add students to ELA class
        for student in ela_students_from_math:
            ela_class.students.append(student)
        
        # Find students not in math or already in ELA
        remaining_students = [s for s in students if s not in math_students and s not in ela_students_from_math]
        
        # Add some more students to ELA to reach ~90% enrollment
        ela_target_count = max(1, int(total_students * 0.9))
        current_ela_count = len(ela_students_from_math)
        additional_ela_needed = max(0, ela_target_count - current_ela_count)
        
        if remaining_students and additional_ela_needed > 0:
            additional_ela_students = random.sample(
                remaining_students, 
                min(additional_ela_needed, len(remaining_students))
            )
            for student in additional_ela_students:
                ela_class.students.append(student)
        
        # Commit enrollments
        db.session.commit()
        
        # Calculate actual overlap
        math_student_ids = {s.id for s in math_class.students}
        ela_student_ids = {s.id for s in ela_class.students}
        overlap_ids = math_student_ids.intersection(ela_student_ids)
        
        overlap_percentage = (len(overlap_ids) / min(len(math_student_ids), len(ela_student_ids))) * 100 if math_student_ids and ela_student_ids else 0
        
        print(f"   ✅ Created 2 classes:")
        print(f"      • Math: {len(math_class.students)} students enrolled")
        print(f"      • ELA: {len(ela_class.students)} students enrolled")
        print(f"      • Student overlap: {len(overlap_ids)} students ({overlap_percentage:.1f}%)")
        print(f"      • Total unique students across classes: {len(math_student_ids.union(ela_student_ids))}")
        print("   📚 Classes seeding completed successfully!")

if __name__ == '__main__':
    seed_classes() 