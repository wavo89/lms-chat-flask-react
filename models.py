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