from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from models import db, MessageBoard

message_board_bp = Blueprint('message_board', __name__)

@message_board_bp.route('/message-board', methods=['GET'])
@login_required
def get_message_board():
    """Get all message board posts."""
    try:
        posts = MessageBoard.query.order_by(MessageBoard.is_pinned.desc(), MessageBoard.created_at.desc()).all()
        return jsonify([post.to_dict() for post in posts]), 200
    except Exception as e:
        print(f"Error fetching message board: {e}")
        return jsonify({"error": "Failed to fetch message board"}), 500

@message_board_bp.route('/message-board', methods=['POST'])
@login_required
def create_message_board_post():
    """Create a new message board post."""
    try:
        data = request.get_json()
        if not data or not data.get('title') or not data.get('content'):
            return jsonify({"error": "Title and content are required"}), 400
        
        post = MessageBoard(
            user_id=current_user.id,
            title=data['title'],
            content=data['content'],
            category=data.get('category', 'research'),
            is_pinned=data.get('is_pinned', False) if current_user.role in ['teacher', 'admin'] else False
        )
        
        db.session.add(post)
        db.session.commit()
        return jsonify(post.to_dict()), 201
    except Exception as e:
        print(f"Error creating message board post: {e}")
        return jsonify({"error": "Failed to create post"}), 500

@message_board_bp.route('/message-board/<int:post_id>', methods=['PUT'])
@login_required
def update_message_board_post(post_id):
    """Update a message board post (only by author or teacher/admin)."""
    try:
        post = MessageBoard.query.get(post_id)
        if not post:
            return jsonify({"error": "Post not found"}), 404
        
        if post.user_id != current_user.id and current_user.role not in ['teacher', 'admin']:
            return jsonify({"error": "Access denied"}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        if 'title' in data:
            post.title = data['title']
        if 'content' in data:
            post.content = data['content']
        if 'category' in data:
            post.category = data['category']
        if 'is_pinned' in data and current_user.role in ['teacher', 'admin']:
            post.is_pinned = data['is_pinned']
        
        post.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify(post.to_dict()), 200
    except Exception as e:
        print(f"Error updating message board post: {e}")
        return jsonify({"error": "Failed to update post"}), 500

@message_board_bp.route('/message-board/<int:post_id>', methods=['DELETE'])
@login_required
def delete_message_board_post(post_id):
    """Delete a message board post (only by author or teacher/admin)."""
    try:
        post = MessageBoard.query.get(post_id)
        if not post:
            return jsonify({"error": "Post not found"}), 404
        
        if post.user_id != current_user.id and current_user.role not in ['teacher', 'admin']:
            return jsonify({"error": "Access denied"}), 403
        
        db.session.delete(post)
        db.session.commit()
        return jsonify({"message": "Post deleted"}), 200
    except Exception as e:
        print(f"Error deleting message board post: {e}")
        return jsonify({"error": "Failed to delete post"}), 500 