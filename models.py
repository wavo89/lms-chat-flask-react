from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime, date

db = SQLAlchemy()
bcrypt = Bcrypt()

# Association table for many-to-many relationship between students and classes
student_classes = db.Table('student_classes',
    db.Column('student_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id'), primary_key=True),
    db.Column('enrolled_at', db.DateTime, default=datetime.utcnow)
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'student', 'teacher', 'admin'
    student_id = db.Column(db.String(20), unique=True, nullable=True)  # For students only
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships for classes (many-to-many for students)
    enrolled_classes = db.relationship('Class', secondary=student_classes, back_populates='students')

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Check if the provided password matches the user's password."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert user object to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'student_id': self.student_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }
    
    def is_teacher(self):
        """Check if user is a teacher."""
        return self.role == 'teacher'
    
    def is_student(self):
        """Check if user is a student."""
        return self.role == 'student'
    
    def is_admin(self):
        """Check if user is an admin."""
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.email}>'


class Class(db.Model):
    __tablename__ = 'classes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., "Math", "ELA"
    description = db.Column(db.Text, nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    teacher = db.relationship('User', backref='taught_classes')
    students = db.relationship('User', secondary=student_classes, back_populates='enrolled_classes')
    
    def to_dict(self):
        """Convert class to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.name if self.teacher else None,
            'student_count': len(self.students),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<Class {self.name}>'


class Assignment(db.Model):
    __tablename__ = 'assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    max_points = db.Column(db.Float, nullable=False, default=100.0)
    due_date = db.Column(db.Date, nullable=True)
    assignment_type = db.Column(db.String(50), nullable=False, default='homework')  # 'homework', 'quiz', 'test', 'project'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    class_obj = db.relationship('Class', backref='assignments')
    
    def to_dict(self):
        """Convert assignment to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'class_id': self.class_id,
            'class_name': self.class_obj.name if self.class_obj else None,
            'max_points': self.max_points,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'assignment_type': self.assignment_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<Assignment {self.name} for {self.class_obj.name if self.class_obj else "Unknown"}>'


class Grade(db.Model):
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    points_earned = db.Column(db.Float, nullable=True)  # Null if not graded yet
    comments = db.Column(db.Text, nullable=True)
    graded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Teacher who graded
    graded_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('User', foreign_keys=[student_id], backref='grades_as_student')
    assignment = db.relationship('Assignment', backref='grades')
    grader = db.relationship('User', foreign_keys=[graded_by], backref='grades_as_grader')
    
    # Unique constraint: one grade per student per assignment
    __table_args__ = (db.UniqueConstraint('student_id', 'assignment_id', name='unique_student_assignment'),)
    
    def to_dict(self):
        """Convert grade to dictionary for JSON serialization."""
        percentage = None
        letter_grade = None
        
        if self.points_earned is not None and self.assignment:
            percentage = (self.points_earned / self.assignment.max_points) * 100
            letter_grade = self.get_letter_grade(percentage)
        
        return {
            'id': self.id,
            'student_id': self.student_id,
            'assignment_id': self.assignment_id,
            'student_name': self.student.name if self.student else None,
            'student_student_id': self.student.student_id if self.student else None,
            'assignment_name': self.assignment.name if self.assignment else None,
            'assignment_max_points': self.assignment.max_points if self.assignment else None,
            'points_earned': self.points_earned,
            'percentage': round(percentage, 1) if percentage is not None else None,
            'letter_grade': letter_grade,
            'comments': self.comments,
            'graded_by': self.graded_by,
            'grader_name': self.grader.name if self.grader else None,
            'graded_at': self.graded_at.isoformat() if self.graded_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def get_letter_grade(percentage):
        """Convert percentage to letter grade."""
        if percentage >= 97:
            return 'A+'
        elif percentage >= 93:
            return 'A'
        elif percentage >= 90:
            return 'A-'
        elif percentage >= 87:
            return 'B+'
        elif percentage >= 83:
            return 'B'
        elif percentage >= 80:
            return 'B-'
        elif percentage >= 77:
            return 'C+'
        elif percentage >= 73:
            return 'C'
        elif percentage >= 70:
            return 'C-'
        elif percentage >= 67:
            return 'D+'
        elif percentage >= 63:
            return 'D'
        elif percentage >= 60:
            return 'D-'
        else:
            return 'F'
    
    def __repr__(self):
        return f'<Grade {self.student.name if self.student else "Unknown"} - {self.assignment.name if self.assignment else "Unknown"}: {self.points_earned}>'


class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False)  # 'present', 'absent', 'tardy', 'excused'
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)  # Added class support
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('User', foreign_keys=[student_id], backref='attendance_as_student')
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref='attendance_as_teacher')
    class_obj = db.relationship('Class', backref='attendance_records')
    
    # Unique constraint: one record per student per date per class
    __table_args__ = (db.UniqueConstraint('student_id', 'date', 'class_id', name='unique_student_date_class'),)
    
    def to_dict(self):
        """Convert attendance record to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'status': self.status,
            'student_id': self.student_id,
            'teacher_id': self.teacher_id,
            'class_id': self.class_id,
            'student_name': self.student.name if self.student else None,
            'student_student_id': self.student.student_id if self.student else None,
            'teacher_name': self.teacher.name if self.teacher else None,
            'class_name': self.class_obj.name if self.class_obj else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def get_valid_statuses():
        """Get list of valid attendance statuses."""
        return ['present', 'absent', 'tardy', 'excused']
    
    def __repr__(self):
        return f'<AttendanceRecord {self.student_id} on {self.date}: {self.status}>'


class ChatHistory(db.Model):
    __tablename__ = 'chat_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.String(255), nullable=True)  # To group related conversations
    
    # Relationship
    user = db.relationship('User', backref='chat_history')
    
    def to_dict(self):
        """Convert chat history to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'user_student_id': self.user.student_id if self.user else None,
            'message': self.message,
            'response': self.response,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'session_id': self.session_id
        }
    
    def __repr__(self):
        return f'<ChatHistory {self.user.name if self.user else "Unknown"} at {self.timestamp}>'


class MessageBoard(db.Model):
    __tablename__ = 'message_board'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), default='research')  # research, announcement, question, etc.
    is_pinned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='message_board_posts')
    
    def to_dict(self):
        """Convert message board post to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'user_role': self.user.role if self.user else None,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'is_pinned': self.is_pinned,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<MessageBoard "{self.title}" by {self.user.name if self.user else "Unknown"}>'


class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(50), default='todo')  # todo, in_progress, completed, cancelled
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    due_date = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assignee = db.relationship('User', foreign_keys=[assigned_to], backref='assigned_tasks')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_tasks')
    
    def to_dict(self):
        """Convert task to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'assigned_to': self.assigned_to,
            'assigned_to_name': self.assignee.name if self.assignee else None,
            'created_by': self.created_by,
            'created_by_name': self.creator.name if self.creator else None,
            'status': self.status,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Task "{self.title}" - {self.status}>'


class Quiz(db.Model):
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)
    is_published = db.Column(db.Boolean, default=False)
    time_limit = db.Column(db.Integer, nullable=True)  # in minutes
    max_attempts = db.Column(db.Integer, default=1)
    due_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref='created_quizzes')
    class_obj = db.relationship('Class', backref='quizzes')
    
    def to_dict(self):
        """Convert quiz to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_by': self.created_by,
            'created_by_name': self.creator.name if self.creator else None,
            'class_id': self.class_id,
            'class_name': self.class_obj.name if self.class_obj else None,
            'is_published': self.is_published,
            'time_limit': self.time_limit,
            'max_attempts': self.max_attempts,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'question_count': len(self.questions) if hasattr(self, 'questions') else 0
        }
    
    def __repr__(self):
        return f'<Quiz "{self.title}" by {self.creator.name if self.creator else "Unknown"}>'


class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), default='multiple_choice')  # multiple_choice, true_false, short_answer
    points = db.Column(db.Integer, default=1)
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    quiz = db.relationship('Quiz', backref='questions')
    
    def to_dict(self):
        """Convert quiz question to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'points': self.points,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'choices': [choice.to_dict() for choice in self.choices] if hasattr(self, 'choices') else []
        }
    
    def __repr__(self):
        return f'<QuizQuestion {self.id} for Quiz {self.quiz_id}>'


class QuizChoice(db.Model):
    __tablename__ = 'quiz_choices'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('quiz_questions.id'), nullable=False)
    choice_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    order_index = db.Column(db.Integer, default=0)
    
    # Relationship
    question = db.relationship('QuizQuestion', backref='choices')
    
    def to_dict(self):
        """Convert quiz choice to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'question_id': self.question_id,
            'choice_text': self.choice_text,
            'is_correct': self.is_correct,
            'order_index': self.order_index
        }
    
    def __repr__(self):
        return f'<QuizChoice {self.id} for Question {self.question_id}>' 