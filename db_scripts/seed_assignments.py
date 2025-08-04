#!/usr/bin/env python3
"""
Assignments seeding script - creates sample assignments for each class.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta
from flask import Flask
from config import Config
from models import db, Class, Assignment

def create_app():
    """Create Flask app instance for database operations."""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def seed_assignments():
    """Add sample assignments to the database."""
    app = create_app()
    
    with app.app_context():
        print("📝 Seeding assignments...")
        
        # Clear existing assignments first
        print("   🗑️  Clearing existing assignments...")
        existing_assignments = Assignment.query.all()
        if existing_assignments:
            for assignment in existing_assignments:
                db.session.delete(assignment)
            db.session.commit()
            print(f"   ✅ Removed {len(existing_assignments)} existing assignments")
        else:
            print("   ✅ No existing assignments to remove")
        
        # Get all classes
        classes = Class.query.all()
        if not classes:
            print("   ⚠️  No classes found. Please run seed_classes.py first.")
            return
        
        # Define assignments for each class
        assignments_data = {
            'Math': [
                {
                    'name': 'Algebra Quiz #1',
                    'description': 'Basic algebraic equations and solving for variables',
                    'max_points': 50.0,
                    'assignment_type': 'quiz',
                    'due_date': date.today() - timedelta(days=10)
                },
                {
                    'name': 'Geometry Project',
                    'description': 'Calculate areas and perimeters of various shapes in a real-world context',
                    'max_points': 100.0,
                    'assignment_type': 'project',
                    'due_date': date.today() - timedelta(days=5)
                },
                {
                    'name': 'Word Problems Homework',
                    'description': 'Practice solving multi-step word problems involving fractions and decimals',
                    'max_points': 75.0,
                    'assignment_type': 'homework',
                    'due_date': date.today() + timedelta(days=3)
                }
            ],
            'ELA': [
                {
                    'name': 'Character Analysis Essay',
                    'description': 'Write a 3-paragraph essay analyzing the main character from our current novel',
                    'max_points': 100.0,
                    'assignment_type': 'test',
                    'due_date': date.today() - timedelta(days=12)
                },
                {
                    'name': 'Vocabulary Quiz #2',
                    'description': 'Definitions and usage of vocabulary words from chapters 5-8',
                    'max_points': 40.0,
                    'assignment_type': 'quiz',
                    'due_date': date.today() - timedelta(days=7)
                },
                {
                    'name': 'Creative Writing Assignment',
                    'description': 'Write a short story (500-750 words) using at least 5 vocabulary words',
                    'max_points': 85.0,
                    'assignment_type': 'homework',
                    'due_date': date.today() + timedelta(days=5)
                }
            ]
        }
        
        created_count = 0
        
        for class_obj in classes:
            if class_obj.name in assignments_data:
                print(f"   📚 Creating assignments for {class_obj.name}...")
                
                for assignment_data in assignments_data[class_obj.name]:
                    assignment = Assignment(
                        name=assignment_data['name'],
                        description=assignment_data['description'],
                        class_id=class_obj.id,
                        max_points=assignment_data['max_points'],
                        due_date=assignment_data['due_date'],
                        assignment_type=assignment_data['assignment_type']
                    )
                    db.session.add(assignment)
                    created_count += 1
                
                print(f"      ✅ Created {len(assignments_data[class_obj.name])} assignments")
        
        # Commit all assignments
        db.session.commit()
        
        print(f"   ✅ Created {created_count} total assignments across {len(classes)} classes")
        print("   📝 Assignments seeding completed successfully!")

if __name__ == '__main__':
    seed_assignments() 