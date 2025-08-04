#!/usr/bin/env python3
"""
Grades seeding script - creates realistic grades for students in assignments.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from datetime import datetime
from flask import Flask
from config import Config
from models import db, User, Class, Assignment, Grade

def create_app():
    """Create Flask app instance for database operations."""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def seed_grades():
    """Add realistic grades to the database."""
    app = create_app()
    
    with app.app_context():
        print("📊 Seeding grades...")
        
        # Clear existing grades first
        print("   🗑️  Clearing existing grades...")
        existing_grades = Grade.query.all()
        if existing_grades:
            for grade in existing_grades:
                db.session.delete(grade)
            db.session.commit()
            print(f"   ✅ Removed {len(existing_grades)} existing grades")
        else:
            print("   ✅ No existing grades to remove")
        
        # Get all assignments and classes
        assignments = Assignment.query.all()
        if not assignments:
            print("   ⚠️  No assignments found. Please run seed_assignments.py first.")
            return
        
        # Get teacher for grader
        teacher = User.query.filter_by(role='teacher').first()
        if not teacher:
            print("   ⚠️  No teachers found. Please run seed_teacher.py first.")
            return
        
        created_count = 0
        
        # Define student performance patterns
        # Some students are consistent high performers, others struggle, some are average
        all_students = User.query.filter_by(role='student').all()
        
        if not all_students:
            print("   ⚠️  No students found. Please run seed_student.py first.")
            return
        
        # Categorize students by performance
        high_performers = random.sample(all_students, min(5, len(all_students) // 4))  # Top 25%
        struggling_students = random.sample([s for s in all_students if s not in high_performers], min(4, len(all_students) // 5))  # Some struggling students
        average_students = [s for s in all_students if s not in high_performers and s not in struggling_students]
        
        print(f"   📈 Performance distribution:")
        print(f"      • High performers: {len(high_performers)} students")
        print(f"      • Struggling students: {len(struggling_students)} students") 
        print(f"      • Average students: {len(average_students)} students")
        
        for assignment in assignments:
            print(f"   📝 Grading {assignment.name} ({assignment.class_obj.name})...")
            
            # Get students enrolled in this class
            enrolled_students = assignment.class_obj.students
            
            for student in enrolled_students:
                # Determine base performance level
                if student in high_performers:
                    # High performers: 85-100% range, weighted toward higher end
                    base_percentage = random.uniform(85, 100)
                    # Add some variation based on assignment type
                    if assignment.assignment_type == 'quiz':
                        base_percentage = min(100, base_percentage + random.uniform(-5, 5))
                    elif assignment.assignment_type == 'project':
                        base_percentage = min(100, base_percentage + random.uniform(-3, 8))  # Projects tend to be higher
                    elif assignment.assignment_type == 'test':
                        base_percentage = max(75, base_percentage - random.uniform(0, 10))  # Tests can be harder
                
                elif student in struggling_students:
                    # Struggling students: 45-75% range
                    base_percentage = random.uniform(45, 75)
                    # Projects might be slightly better for hands-on learners
                    if assignment.assignment_type == 'project':
                        base_percentage = min(85, base_percentage + random.uniform(5, 15))
                    elif assignment.assignment_type == 'test':
                        base_percentage = max(35, base_percentage - random.uniform(5, 15))
                
                else:
                    # Average students: 70-90% range
                    base_percentage = random.uniform(70, 90)
                    # Some variation by type
                    if assignment.assignment_type == 'quiz':
                        base_percentage = base_percentage + random.uniform(-8, 8)
                    elif assignment.assignment_type == 'project':
                        base_percentage = min(95, base_percentage + random.uniform(0, 10))
                    elif assignment.assignment_type == 'test':
                        base_percentage = base_percentage + random.uniform(-10, 5)
                
                # Ensure percentage is within bounds
                base_percentage = max(0, min(100, base_percentage))
                
                # Calculate points earned
                points_earned = (base_percentage / 100) * assignment.max_points
                points_earned = round(points_earned, 1)
                
                # Some assignments might not be graded yet (10% chance for recent assignments)
                is_graded = True
                if assignment.due_date and assignment.due_date > datetime.now().date():
                    # Future assignments - 70% chance not graded yet
                    is_graded = random.random() < 0.3
                elif assignment.due_date and (datetime.now().date() - assignment.due_date).days < 3:
                    # Very recent assignments - 40% chance not graded yet
                    is_graded = random.random() < 0.6
                
                # Create grade record
                grade = Grade(
                    student_id=student.id,
                    assignment_id=assignment.id,
                    points_earned=points_earned if is_graded else None,
                    graded_by=teacher.id if is_graded else None,
                    graded_at=datetime.now() if is_graded else None,
                    comments=get_comment(base_percentage, assignment.assignment_type) if is_graded and random.random() < 0.3 else None
                )
                
                db.session.add(grade)
                created_count += 1
            
            print(f"      ✅ Created {len(enrolled_students)} grades")
        
        # Commit all grades
        db.session.commit()
        
        # Calculate some statistics
        graded_count = Grade.query.filter(Grade.points_earned.isnot(None)).count()
        ungraded_count = Grade.query.filter(Grade.points_earned.is_(None)).count()
        
        print(f"   ✅ Created {created_count} total grade records")
        print(f"      • Graded assignments: {graded_count}")
        print(f"      • Pending grades: {ungraded_count}")
        print("   📊 Grades seeding completed successfully!")

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
    seed_grades() 