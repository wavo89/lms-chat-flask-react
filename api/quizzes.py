from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from models import db, Quiz
from .utils import teacher_required

quizzes_bp = Blueprint('quizzes', __name__)

@quizzes_bp.route('/quizzes', methods=['GET'])
@login_required
def get_quizzes():
    """Get quizzes."""
    try:
        if current_user.role in ['teacher', 'admin']:
            quizzes = Quiz.query.filter_by(created_by=current_user.id).order_by(Quiz.created_at.desc()).all()
        else:
            student_classes = [c.id for c in current_user.enrolled_classes]
            quizzes = Quiz.query.filter(
                Quiz.is_published == True,
                Quiz.class_id.in_(student_classes)
            ).order_by(Quiz.due_date.asc().nullslast()).all()
        
        return jsonify([quiz.to_dict() for quiz in quizzes]), 200
    except Exception as e:
        print(f"Error fetching quizzes: {e}")
        return jsonify({"error": "Failed to fetch quizzes"}), 500

@quizzes_bp.route('/quizzes', methods=['POST'])
@login_required
@teacher_required
def create_quiz():
    """Create a new quiz."""
    try:
        data = request.get_json()
        if not data or not data.get('title'):
            return jsonify({"error": "Title is required"}), 400
        
        due_date = None
        if data.get('due_date'):
            due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        
        quiz = Quiz(
            title=data['title'],
            description=data.get('description'),
            created_by=current_user.id,
            class_id=data.get('class_id'),
            time_limit=data.get('time_limit'),
            max_attempts=data.get('max_attempts', 1),
            due_date=due_date
        )
        
        db.session.add(quiz)
        db.session.commit()
        return jsonify(quiz.to_dict()), 201
    except Exception as e:
        print(f"Error creating quiz: {e}")
        return jsonify({"error": "Failed to create quiz"}), 500

@quizzes_bp.route('/quizzes/<int:quiz_id>', methods=['PUT'])
@login_required
@teacher_required
def update_quiz(quiz_id):
    """Update a quiz."""
    try:
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({"error": "Quiz not found"}), 404
        
        if quiz.created_by != current_user.id:
            return jsonify({"error": "Access denied"}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        if 'title' in data:
            quiz.title = data['title']
        if 'description' in data:
            quiz.description = data['description']
        if 'class_id' in data:
            quiz.class_id = data['class_id']
        if 'is_published' in data:
            quiz.is_published = data['is_published']
        if 'time_limit' in data:
            quiz.time_limit = data['time_limit']
        if 'max_attempts' in data:
            quiz.max_attempts = data['max_attempts']
        if 'due_date' in data:
            quiz.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00')) if data['due_date'] else None
        
        quiz.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify(quiz.to_dict()), 200
    except Exception as e:
        print(f"Error updating quiz: {e}")
        return jsonify({"error": "Failed to update quiz"}), 500 