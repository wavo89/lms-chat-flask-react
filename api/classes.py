from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Class, Assignment, User
from .utils import teacher_required

classes_bp = Blueprint('classes', __name__)

@classes_bp.route('/classes', methods=['GET'])
@login_required
def get_classes():
    """Get all active classes."""
    try:
        classes = Class.query.filter_by(is_active=True).all()
        return jsonify([cls.to_dict() for cls in classes]), 200
    except Exception as e:
        print(f"Error fetching classes: {e}")
        return jsonify({"error": "Failed to fetch classes"}), 500

@classes_bp.route('/classes', methods=['POST'])
@login_required
@teacher_required
def create_class():
    """Create a new class."""
    try:
        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({"error": "Class name is required"}), 400
        
        new_class = Class(
            name=data['name'],
            description=data.get('description'),
            teacher_id=current_user.id,
            is_active=data.get('is_active', True)
        )
        
        db.session.add(new_class)
        db.session.commit()
        
        return jsonify(new_class.to_dict()), 201
    except Exception as e:
        print(f"Error creating class: {e}")
        return jsonify({"error": "Failed to create class"}), 500

@classes_bp.route('/classes/<int:class_id>', methods=['PUT'])
@login_required
@teacher_required
def update_class(class_id):
    """Update a class."""
    try:
        class_obj = Class.query.get(class_id)
        if not class_obj:
            return jsonify({"error": "Class not found"}), 404
        
        if class_obj.teacher_id != current_user.id and current_user.role != 'admin':
            return jsonify({"error": "Access denied"}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        if 'name' in data:
            class_obj.name = data['name']
        if 'description' in data:
            class_obj.description = data['description']
        if 'is_active' in data:
            class_obj.is_active = data['is_active']
        
        db.session.commit()
        return jsonify(class_obj.to_dict()), 200
    except Exception as e:
        print(f"Error updating class: {e}")
        return jsonify({"error": "Failed to update class"}), 500

@classes_bp.route('/classes/<int:class_id>/assignments', methods=['GET'])
@login_required
def get_class_assignments(class_id):
    """Get assignments for a specific class."""
    try:
        assignments = Assignment.query.filter_by(class_id=class_id, is_active=True).order_by(Assignment.due_date).all()
        return jsonify([assignment.to_dict() for assignment in assignments]), 200
    except Exception as e:
        print(f"Error fetching assignments: {e}")
        return jsonify({"error": "Failed to get assignments"}), 500

@classes_bp.route('/classes/<int:class_id>/students', methods=['GET'])
@login_required
def get_class_students(class_id):
    """Get students enrolled in a specific class."""
    try:
        class_obj = Class.query.get(class_id)
        if not class_obj:
            return jsonify({"error": "Class not found"}), 404
        
        students = class_obj.students
        return jsonify({
            "students": [{
                "id": student.id,
                "name": student.name,
                "email": student.email,
                "student_id": student.student_id
            } for student in students]
        }), 200
    except Exception as e:
        print(f"Error fetching class students: {e}")
        return jsonify({"error": "Failed to fetch class students"}), 500

@classes_bp.route('/classes/<int:class_id>/enroll', methods=['POST'])
@login_required
@teacher_required
def enroll_student(class_id):
    """Enroll a student in a class."""
    try:
        data = request.get_json()
        if not data or not data.get('student_id'):
            return jsonify({"error": "Student ID is required"}), 400
        
        class_obj = Class.query.get(class_id)
        if not class_obj:
            return jsonify({"error": "Class not found"}), 404
        
        student = User.query.get(data['student_id'])
        if not student or student.role != 'student':
            return jsonify({"error": "Student not found"}), 404
        
        if student in class_obj.students:
            return jsonify({"error": "Student already enrolled"}), 409
        
        class_obj.students.append(student)
        db.session.commit()
        
        return jsonify({"message": "Student enrolled successfully"}), 200
    except Exception as e:
        print(f"Error enrolling student: {e}")
        return jsonify({"error": "Failed to enroll student"}), 500

@classes_bp.route('/classes/<int:class_id>/unenroll', methods=['POST'])
@login_required
@teacher_required
def unenroll_student(class_id):
    """Unenroll a student from a class."""
    try:
        data = request.get_json()
        if not data or not data.get('student_id'):
            return jsonify({"error": "Student ID is required"}), 400
        
        class_obj = Class.query.get(class_id)
        if not class_obj:
            return jsonify({"error": "Class not found"}), 404
        
        student = User.query.get(data['student_id'])
        if not student:
            return jsonify({"error": "Student not found"}), 404
        
        if student not in class_obj.students:
            return jsonify({"error": "Student not enrolled in this class"}), 409
        
        class_obj.students.remove(student)
        db.session.commit()
        
        return jsonify({"message": "Student unenrolled successfully"}), 200
    except Exception as e:
        print(f"Error unenrolling student: {e}")
        return jsonify({"error": "Failed to unenroll student"}), 500 