from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from models import db, Task
from .utils import teacher_required

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    """Get tasks for current user or all tasks if teacher."""
    try:
        if current_user.role in ['teacher', 'admin']:
            tasks = Task.query.order_by(Task.due_date.asc().nullslast(), Task.created_at.desc()).all()
        else:
            tasks = Task.query.filter_by(assigned_to=current_user.id).order_by(Task.due_date.asc().nullslast(), Task.created_at.desc()).all()
        
        return jsonify([task.to_dict() for task in tasks]), 200
    except Exception as e:
        print(f"Error fetching tasks: {e}")
        return jsonify({"error": "Failed to fetch tasks"}), 500

@tasks_bp.route('/tasks', methods=['POST'])
@login_required
def create_task():
    """Create a new task."""
    try:
        data = request.get_json()
        if not data or not data.get('title'):
            return jsonify({"error": "Title is required"}), 400
        
        due_date = None
        if data.get('due_date'):
            due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        
        task = Task(
            title=data['title'],
            description=data.get('description'),
            assigned_to=data.get('assigned_to'),
            created_by=current_user.id,
            status=data.get('status', 'todo'),
            priority=data.get('priority', 'medium'),
            due_date=due_date
        )
        
        db.session.add(task)
        db.session.commit()
        return jsonify(task.to_dict()), 201
    except Exception as e:
        print(f"Error creating task: {e}")
        return jsonify({"error": "Failed to create task"}), 500

@tasks_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    """Update a task."""
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404
        
        if task.created_by != current_user.id and task.assigned_to != current_user.id and current_user.role not in ['teacher', 'admin']:
            return jsonify({"error": "Access denied"}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'assigned_to' in data and current_user.role in ['teacher', 'admin']:
            task.assigned_to = data['assigned_to']
        if 'status' in data:
            task.status = data['status']
            if data['status'] == 'completed' and not task.completed_at:
                task.completed_at = datetime.utcnow()
            elif data['status'] != 'completed':
                task.completed_at = None
        if 'priority' in data:
            task.priority = data['priority']
        if 'due_date' in data:
            task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00')) if data['due_date'] else None
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify(task.to_dict()), 200
    except Exception as e:
        print(f"Error updating task: {e}")
        return jsonify({"error": "Failed to update task"}), 500

@tasks_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    """Delete a task."""
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({"error": "Task not found"}), 404
        
        if task.created_by != current_user.id and current_user.role not in ['teacher', 'admin']:
            return jsonify({"error": "Access denied"}), 403
        
        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": "Task deleted"}), 200
    except Exception as e:
        print(f"Error deleting task: {e}")
        return jsonify({"error": "Failed to delete task"}), 500 