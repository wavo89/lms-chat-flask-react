from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from models import db, Class, Assignment, Grade, User
from .utils import teacher_required

grades_bp = Blueprint('grades', __name__)

@grades_bp.route('/classes/<int:class_id>/grades', methods=['GET'])
@login_required
def get_class_grades(class_id):
    """Get grades matrix for a specific class."""
    try:
        print(f"Getting grades for class {class_id}")
        
        class_obj = Class.query.get(class_id)
        if not class_obj:
            return jsonify({"error": "Class not found"}), 404
        
        # Get assignments for this class
        assignments = Assignment.query.filter_by(class_id=class_id, is_active=True).order_by(Assignment.due_date).all()
        print(f"Found {len(assignments)} assignments")
        
        # Get students enrolled in this class
        students = class_obj.students
        print(f"Found {len(students)} students")
        
        # Get all grades for this class
        assignment_ids = [a.id for a in assignments]
        grades = Grade.query.filter(Grade.assignment_id.in_(assignment_ids)).all()
        print(f"Found {len(grades)} grade records")
        
        # Organize grades by student and assignment
        grades_dict = {}
        for grade in grades:
            if grade.student_id not in grades_dict:
                grades_dict[grade.student_id] = {}
            grades_dict[grade.student_id][grade.assignment_id] = grade.to_dict()
        
        # Build response with students and their grades
        response = {
            "class": class_obj.to_dict(),
            "assignments": [assignment.to_dict() for assignment in assignments],
            "students": [],
            "grades": grades_dict
        }
        
        for student in students:
            student_data = {
                "id": student.id,
                "name": student.name,
                "student_id": student.student_id,
                "grades": grades_dict.get(student.id, {})
            }
            response["students"].append(student_data)
        
        print(f"Returning response with {len(response['students'])} students")
        return jsonify(response), 200
    except Exception as e:
        print(f"Error getting class grades: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Failed to get class grades"}), 500

@grades_bp.route('/grades/<int:grade_id>', methods=['PUT'])
@login_required
@teacher_required
def update_grade(grade_id):
    """Update a specific grade."""
    try:
        print(f"Updating grade {grade_id}")
        
        grade = Grade.query.get(grade_id)
        if not grade:
            print(f"Grade {grade_id} not found")
            return jsonify({"error": "Grade not found"}), 404
        
        data = request.get_json()
        if not data:
            print("No data provided")
            return jsonify({"error": "No data provided"}), 400
        
        print(f"Update data: {data}")
        
        # Update grade fields
        if 'points_earned' in data:
            # Convert to int and validate range
            points = data['points_earned']
            if points is not None:
                try:
                    points = int(points)
                    if points < 0 or points > 100:
                        return jsonify({"error": "Points must be between 0 and 100"}), 400
                except (ValueError, TypeError):
                    return jsonify({"error": "Points must be a valid integer"}), 400
            
            grade.points_earned = points
            print(f"Updated points_earned to: {points}")
        
        if 'comments' in data:
            grade.comments = data['comments']
            print(f"Updated comments to: {data['comments']}")
        
        grade.graded_by = current_user.id
        grade.graded_at = datetime.utcnow()
        grade.updated_at = datetime.utcnow()
        
        db.session.commit()
        print(f"Grade {grade_id} updated successfully")
        
        return jsonify(grade.to_dict()), 200
    except Exception as e:
        print(f"Error updating grade: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"error": "Failed to update grade"}), 500

@grades_bp.route('/grades', methods=['POST'])
@login_required
@teacher_required
def create_grade():
    """Create a new grade record."""
    try:
        data = request.get_json()
        if not data or not data.get('student_id') or not data.get('assignment_id'):
            return jsonify({"error": "Student ID and assignment ID are required"}), 400
        
        # Check if grade already exists
        existing_grade = Grade.query.filter_by(
            student_id=data['student_id'],
            assignment_id=data['assignment_id']
        ).first()
        
        if existing_grade:
            return jsonify({"error": "Grade already exists for this student and assignment"}), 409
        
        # Create new grade
        grade = Grade(
            student_id=data['student_id'],
            assignment_id=data['assignment_id'],
            points_earned=data.get('points_earned'),
            comments=data.get('comments'),
            graded_by=current_user.id,
            graded_at=datetime.utcnow()
        )
        
        db.session.add(grade)
        db.session.commit()
        
        return jsonify(grade.to_dict()), 201
    except Exception as e:
        print(f"Error creating grade: {e}")
        return jsonify({"error": "Failed to create grade"}), 500 