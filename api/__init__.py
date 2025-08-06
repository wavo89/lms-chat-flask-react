from flask import Blueprint
from .auth import auth_bp
from .classes import classes_bp
from .grades import grades_bp
from .attendance import attendance_bp
from .tasks import tasks_bp
from .quizzes import quizzes_bp
from .chat import chat_bp
from .message_board import message_board_bp

def register_blueprints(app):
    """Register all API blueprints with the Flask app."""
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(classes_bp, url_prefix='/api')
    app.register_blueprint(grades_bp, url_prefix='/api')
    app.register_blueprint(attendance_bp, url_prefix='/api')
    app.register_blueprint(tasks_bp, url_prefix='/api')
    app.register_blueprint(quizzes_bp, url_prefix='/api')
    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(message_board_bp, url_prefix='/api') 