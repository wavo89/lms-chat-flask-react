from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime, date

db = SQLAlchemy()
bcrypt = Bcrypt()

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


class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False)  # 'present', 'absent', 'tardy', 'excused'
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = db.relationship('User', foreign_keys=[student_id], backref='attendance_as_student')
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref='attendance_as_teacher')
    
    # Unique constraint: one record per student per date
    __table_args__ = (db.UniqueConstraint('student_id', 'date', name='unique_student_date'),)
    
    def to_dict(self):
        """Convert attendance record to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'date': self.date.isoformat() if self.date else None,
            'status': self.status,
            'student_id': self.student_id,
            'teacher_id': self.teacher_id,
            'student_name': self.student.name if self.student else None,
            'student_student_id': self.student.student_id if self.student else None,
            'teacher_name': self.teacher.name if self.teacher else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def get_valid_statuses():
        """Get list of valid attendance statuses."""
        return ['present', 'absent', 'tardy', 'excused']
    
    def __repr__(self):
        return f'<AttendanceRecord {self.student_id} on {self.date}: {self.status}>' 