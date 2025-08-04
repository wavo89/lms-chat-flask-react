from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
import os
from datetime import datetime, date
from openai import OpenAI
from config import Config
from models import db, bcrypt, User, AttendanceRecord, Class, Assignment, Grade
import requests
import json

app = Flask(__name__, static_folder='frontend/build')
app.config.from_object(Config)

# Initialize extensions
CORS(app, supports_credentials=True)  # Enable credentials for authentication
db.init_app(app)
bcrypt.init_app(app)

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Authorization decorator
def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_teacher() and not current_user.is_admin():
            return jsonify({"error": "Teacher access required"}), 403
        return f(*args, **kwargs)
    return decorated_function

# Sample data (keep for compatibility)
users_data = [
    {"id": 1, "name": "John Doe", "email": "john@example.com"},
    {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
    {"id": 3, "name": "Bob Johnson", "email": "bob@example.com"}
]

# Serve React static files
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# Authentication Routes
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password are required"}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if user and user.check_password(data['password']):
        login_user(user)
        return jsonify({
            "message": "Login successful",
            "user": user.to_dict()
        }), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successful"}), 200

@app.route('/api/me', methods=['GET'])
@login_required
def get_current_user():
    return jsonify({"user": current_user.to_dict()}), 200

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data or 'name' not in data:
        return jsonify({"error": "Email, password, and name are required"}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "User with this email already exists"}), 409
    
    # Create new user
    user = User(email=data['email'], name=data['name'])
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    login_user(user)
    return jsonify({
        "message": "Registration successful",
        "user": user.to_dict()
    }), 201

# API Routes
@app.route('/api/')
def api_home():
    return jsonify({"message": "Flask API is running!", "version": "1.0"})

@app.route('/api/users', methods=['GET'])
@login_required
def get_users():
    # Get real users from database
    db_users = User.query.all()
    users_list = [user.to_dict() for user in db_users]
    return jsonify({"users": users_list, "count": len(users_list)})

@app.route('/api/students', methods=['GET'])
@login_required
def get_students():
    # Get only students from database
    students = User.query.filter_by(role='student').order_by(User.student_id).all()
    students_list = [student.to_dict() for student in students]
    return jsonify({"students": students_list, "count": len(students_list)})

@app.route('/api/teachers', methods=['GET'])
@login_required
def get_teachers():
    # Get only teachers from database
    teachers = User.query.filter_by(role='teacher').order_by(User.name).all()
    teachers_list = [teacher.to_dict() for teacher in teachers]
    return jsonify({"teachers": teachers_list, "count": len(teachers_list)})

@app.route('/api/users/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({"user": user.to_dict()})
    return jsonify({"error": "User not found"}), 404

@app.route('/api/users', methods=['POST'])
@login_required
def create_user():
    data = request.get_json()
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({"error": "Name and email are required"}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "User with this email already exists"}), 409
    
    # Get role from request or default to student
    role = data.get('role', 'student')
    if role not in ['student', 'teacher', 'admin']:
        return jsonify({"error": "Invalid role"}), 400
    
    # For students, check if student_id is provided and unique
    student_id = None
    if role == 'student':
        student_id = data.get('student_id')
        if not student_id:
            return jsonify({"error": "Student ID is required for students"}), 400
        if User.query.filter_by(student_id=student_id).first():
            return jsonify({"error": "Student ID already exists"}), 409
    
    # Create new user
    user = User(
        email=data['email'], 
        name=data['name'],
        role=role,
        student_id=student_id
    )
    user.set_password('TempPass123')  # Default password
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        "user": user.to_dict(),
        "message": f"{role.title()} created successfully"
    }), 201

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"})

# Attendance Routes
@app.route('/api/attendance', methods=['GET'])
@login_required
@teacher_required
def get_attendance():
    date_str = request.args.get('date')
    class_id = request.args.get('class_id')
    
    if not date_str:
        date_str = date.today().isoformat()
    
    try:
        attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Get students based on class filter
    if class_id:
        try:
            class_id = int(class_id)
            class_obj = Class.query.get(class_id)
            if not class_obj:
                return jsonify({"error": "Class not found"}), 404
            students = class_obj.students
        except ValueError:
            return jsonify({"error": "Invalid class_id"}), 400
    else:
        # Get all students if no class filter
        students = User.query.filter_by(role='student').order_by(User.student_id).all()
    
    # Sort students by student_id
    students = sorted(students, key=lambda s: s.student_id or '')
    
    # Get existing attendance records for this date and class
    if class_id:
        records = AttendanceRecord.query.filter_by(
            date=attendance_date, 
            class_id=class_id
        ).all()
    else:
        records = AttendanceRecord.query.filter_by(
            date=attendance_date,
            class_id=None  # Legacy records without class
        ).all()
    
    records_dict = {record.student_id: record for record in records}
    
    # Build response with students and their attendance status
    attendance_data = []
    for student in students:
        record = records_dict.get(student.id)
        attendance_data.append({
            'student_id': student.id,
            'student_student_id': student.student_id,
            'name': student.name,
            'email': student.email,
            'status': record.status if record else '',
            'record_id': record.id if record else None
        })
    
    return jsonify({
        "date": date_str,
        "class_id": class_id,
        "class_name": class_obj.name if class_id and class_obj else None,
        "attendance": attendance_data,
        "count": len(attendance_data)
    })

@app.route('/api/attendance', methods=['POST'])
@login_required
@teacher_required
def save_attendance():
    data = request.get_json()
    if not data or 'date' not in data or 'records' not in data:
        return jsonify({"error": "Date and records are required"}), 400
    
    try:
        attendance_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    class_id = data.get('class_id')  # Optional class_id
    
    valid_statuses = AttendanceRecord.get_valid_statuses()
    records_data = data['records']
    
    saved_records = []
    errors = []
    
    for record_data in records_data:
        student_id = record_data.get('student_id')
        status = record_data.get('status', '').lower()
        
        # Skip empty statuses
        if not status:
            continue
            
        if status not in valid_statuses:
            errors.append(f"Invalid status '{status}' for student {student_id}")
            continue
        
        # Check if student exists
        student = User.query.filter_by(id=student_id, role='student').first()
        if not student:
            errors.append(f"Student {student_id} not found")
            continue
        
        # Create or update attendance record
        filter_params = {
            'student_id': student_id,
            'date': attendance_date
        }
        if class_id:
            filter_params['class_id'] = class_id
        else:
            filter_params['class_id'] = None
            
        existing_record = AttendanceRecord.query.filter_by(**filter_params).first()
        
        if existing_record:
            existing_record.status = status
            existing_record.teacher_id = current_user.id
            existing_record.updated_at = datetime.utcnow()
            record = existing_record
        else:
            record = AttendanceRecord(
                date=attendance_date,
                status=status,
                student_id=student_id,
                teacher_id=current_user.id,
                class_id=class_id if class_id else None
            )
            db.session.add(record)
        
        saved_records.append(record)
    
    try:
        db.session.commit()
        return jsonify({
            "message": f"Saved {len(saved_records)} attendance records",
            "saved_count": len(saved_records),
            "errors": errors,
            "date": data['date'],
            "class_id": class_id
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save attendance: {str(e)}"}), 500

@app.route('/api/classes', methods=['GET'])
@login_required
def get_classes():
    """Get all classes."""
    try:
        classes = Class.query.filter_by(is_active=True).all()
        return jsonify([cls.to_dict() for cls in classes]), 200
    except Exception as e:
        print(f"Error getting classes: {e}")
        return jsonify({"error": "Failed to get classes"}), 500

@app.route('/api/classes/<int:class_id>/assignments', methods=['GET'])
@login_required
def get_class_assignments(class_id):
    """Get all assignments for a specific class."""
    try:
        class_obj = Class.query.get(class_id)
        if not class_obj:
            return jsonify({"error": "Class not found"}), 404
        
        assignments = Assignment.query.filter_by(class_id=class_id, is_active=True).order_by(Assignment.due_date).all()
        return jsonify([assignment.to_dict() for assignment in assignments]), 200
    except Exception as e:
        print(f"Error getting assignments: {e}")
        return jsonify({"error": "Failed to get assignments"}), 500

@app.route('/api/classes/<int:class_id>/grades', methods=['GET'])
@login_required
def get_class_grades(class_id):
    """Get grades matrix for a specific class."""
    try:
        class_obj = Class.query.get(class_id)
        if not class_obj:
            return jsonify({"error": "Class not found"}), 404
        
        # Get assignments for this class
        assignments = Assignment.query.filter_by(class_id=class_id, is_active=True).order_by(Assignment.due_date).all()
        
        # Get students enrolled in this class
        students = class_obj.students
        
        # Get all grades for this class
        assignment_ids = [a.id for a in assignments]
        grades = Grade.query.filter(Grade.assignment_id.in_(assignment_ids)).all()
        
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
        
        return jsonify(response), 200
    except Exception as e:
        print(f"Error getting class grades: {e}")
        return jsonify({"error": "Failed to get class grades"}), 500

@app.route('/api/grades/<int:grade_id>', methods=['PUT'])
@login_required
@teacher_required
def update_grade(grade_id):
    """Update a specific grade."""
    try:
        grade = Grade.query.get(grade_id)
        if not grade:
            return jsonify({"error": "Grade not found"}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Update grade fields
        if 'points_earned' in data:
            grade.points_earned = float(data['points_earned']) if data['points_earned'] is not None else None
        
        if 'comments' in data:
            grade.comments = data['comments']
        
        grade.graded_by = current_user.id
        grade.graded_at = datetime.utcnow()
        grade.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(grade.to_dict()), 200
    except Exception as e:
        print(f"Error updating grade: {e}")
        return jsonify({"error": "Failed to update grade"}), 500

# New AI-specific endpoints for function calling
@app.route('/api/ai/attendance-summary', methods=['GET'])
@login_required
def ai_attendance_summary():
    """Get attendance summary for AI assistant - recent days with statistics."""
    try:
        # Get date range (last 7 weekdays by default, or custom range)
        days = int(request.args.get('days', 7))
        end_date = date.today()
        
        # Get weekdays in range
        attendance_dates = []
        current_check = end_date
        
        from datetime import timedelta
        
        for i in range(days * 2):  # Check more days to get enough weekdays
            if current_check.weekday() < 5:  # Monday=0, Sunday=6
                attendance_dates.append(current_check)
                if len(attendance_dates) >= days:
                    break
            current_check = current_check - timedelta(days=1)
        
        attendance_dates.reverse()  # Oldest first
        
        # Get all students
        students = User.query.filter_by(role='student').all()
        if not students:
            return jsonify({"summary": "No students found in the system.", "details": []}), 200
        
        # Get attendance records for the date range
        records = AttendanceRecord.query.filter(
            AttendanceRecord.date.in_(attendance_dates)
        ).all()
        
        # Organize data by student
        student_data = {}
        for student in students:
            student_data[student.id] = {
                'name': student.name,
                'email': student.email,
                'student_id': student.student_id,
                'records': []
            }
        
        for record in records:
            if record.student_id in student_data:
                student_data[record.student_id]['records'].append({
                    'date': record.date.strftime('%Y-%m-%d'),
                    'status': record.status
                })
        
        # Calculate statistics
        total_students = len(students)
        total_days = len(attendance_dates)
        total_possible_records = total_students * total_days
        
        status_counts = {'present': 0, 'absent': 0, 'tardy': 0, 'excused': 0}
        for record in records:
            status_counts[record.status] = status_counts.get(record.status, 0) + 1
        
        # Find students with attendance issues
        problem_students = []
        for student_id, data in student_data.items():
            student_records = data['records']
            if len(student_records) < total_days:
                # Missing records - treat as absent
                missing_days = total_days - len(student_records)
                absent_count = sum(1 for r in student_records if r['status'] == 'absent') + missing_days
            else:
                absent_count = sum(1 for r in student_records if r['status'] == 'absent')
            
            tardy_count = sum(1 for r in student_records if r['status'] == 'tardy')
            attendance_rate = len([r for r in student_records if r['status'] == 'present']) / total_days * 100
            
            if attendance_rate < 80 or absent_count >= 2 or tardy_count >= 3:
                problem_students.append({
                    'name': data['name'],
                    'student_id': data['student_id'],
                    'attendance_rate': round(attendance_rate, 1),
                    'absent_days': absent_count,
                    'tardy_days': tardy_count,
                    'recent_status': student_records[-1]['status'] if student_records else 'no_record'
                })
        
        summary = {
            'date_range': {
                'start': attendance_dates[0].strftime('%Y-%m-%d') if attendance_dates else None,
                'end': attendance_dates[-1].strftime('%Y-%m-%d') if attendance_dates else None,
                'total_days': total_days
            },
            'overall_stats': {
                'total_students': total_students,
                'total_records': len(records),
                'attendance_rate': round(status_counts['present'] / len(records) * 100, 1) if records else 0,
                'status_breakdown': status_counts
            },
            'students_with_issues': problem_students,
            'trends': {
                'chronic_absentees': len([s for s in problem_students if s['absent_days'] >= 3]),
                'frequent_tardies': len([s for s in problem_students if s['tardy_days'] >= 3]),
                'low_attendance': len([s for s in problem_students if s['attendance_rate'] < 80])
            }
        }
        
        return jsonify(summary), 200
        
    except Exception as e:
        print(f"Error getting attendance summary: {e}")
        return jsonify({"error": "Failed to get attendance summary"}), 500

@app.route('/api/ai/student-attendance/<student_id>', methods=['GET'])
@login_required
def ai_student_attendance(student_id):
    """Get detailed attendance for a specific student."""
    try:
        student = User.query.get(student_id)
        if not student or student.role != 'student':
            return jsonify({"error": "Student not found"}), 404
        
        # Get recent attendance records
        days = int(request.args.get('days', 14))
        records = AttendanceRecord.query.filter_by(student_id=student_id).order_by(AttendanceRecord.date.desc()).limit(days).all()
        
        attendance_history = []
        for record in records:
            attendance_history.append({
                'date': record.date.strftime('%Y-%m-%d'),
                'day_of_week': record.date.strftime('%A'),
                'status': record.status
            })
        
        # Calculate student stats
        total_records = len(attendance_history)
        if total_records > 0:
            present_count = sum(1 for r in attendance_history if r['status'] == 'present')
            absent_count = sum(1 for r in attendance_history if r['status'] == 'absent')
            tardy_count = sum(1 for r in attendance_history if r['status'] == 'tardy')
            excused_count = sum(1 for r in attendance_history if r['status'] == 'excused')
            
            attendance_rate = (present_count / total_records) * 100
        else:
            present_count = absent_count = tardy_count = excused_count = 0
            attendance_rate = 0
        
        student_info = {
            'name': student.name,
            'email': student.email,
            'student_id': student.student_id,
            'attendance_rate': round(attendance_rate, 1),
            'total_days_recorded': total_records,
            'status_counts': {
                'present': present_count,
                'absent': absent_count,
                'tardy': tardy_count,
                'excused': excused_count
            },
            'recent_history': attendance_history
        }
        
        return jsonify(student_info), 200
        
    except Exception as e:
        print(f"Error getting student attendance: {e}")
        return jsonify({"error": "Failed to get student attendance"}), 500

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Message is required"}), 400
    
    user_message = data['message']
    user_name = data.get('user', current_user.name)
    user_role = current_user.role
    
    # Define available functions for the AI
    available_functions = [
        {
            "name": "get_attendance_summary",
            "description": "Get overall attendance summary and identify students with attendance issues. Use this for questions about general attendance trends, who has attendance problems, overall statistics, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "description": "Number of recent weekdays to analyze (default: 7)",
                        "default": 7
                    }
                }
            }
        },
        {
            "name": "get_student_attendance",
            "description": "Get detailed attendance information for a specific student. Use this when asked about a particular student's attendance record.",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_name": {
                        "type": "string",
                        "description": "Name of the student to look up"
                    },
                    "days": {
                        "type": "integer", 
                        "description": "Number of recent days to include (default: 14)",
                        "default": 14
                    }
                },
                "required": ["student_name"]
            }
        }
    ]
    
    try:
        # Create initial messages
        messages = [
            {
                "role": "system", 
                "content": f"""You are a helpful AI assistant for a Learning Management System (LMS). You're helping {user_name}, who is a {user_role} in the system.

You have access to real-time attendance data through function calls. When users ask about attendance, use the available functions to get current data rather than making assumptions.

Key guidelines:
- For general attendance questions (who has issues, overall trends), use get_attendance_summary
- For specific student questions, use get_student_attendance with the student's name
- Always provide specific, data-driven insights when attendance data is available
- Be helpful and educational in your responses
- If asking about recent data, the default timeframe is the last 7 weekdays unless specified otherwise
- Focus on actionable insights and patterns in the data"""
            },
            {
                "role": "user", 
                "content": user_message
            }
        ]
        
        # First API call to see if the AI wants to use functions
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            functions=available_functions,
            function_call="auto",
            max_tokens=800,
            temperature=0.7
        )
        
        response_message = response.choices[0].message
        
        # Check if the AI wants to call a function
        if response_message.function_call:
            function_name = response_message.function_call.name
            function_args = json.loads(response_message.function_call.arguments)
            
            # Execute the function call
            if function_name == "get_attendance_summary":
                days = function_args.get('days', 7)
                function_response = requests.get(
                    f'http://localhost:5001/api/ai/attendance-summary?days={days}',
                    cookies=request.cookies
                )
                function_result = function_response.json()
                
            elif function_name == "get_student_attendance":
                student_name = function_args.get('student_name')
                days = function_args.get('days', 14)
                
                # Find student by name
                student = User.query.filter(
                    User.role == 'student',
                    User.name.ilike(f'%{student_name}%')
                ).first()
                
                if student:
                    function_response = requests.get(
                        f'http://localhost:5001/api/ai/student-attendance/{student.id}?days={days}',
                        cookies=request.cookies
                    )
                    function_result = function_response.json()
                else:
                    function_result = {"error": f"Student '{student_name}' not found"}
            
            # Add function call and result to conversation
            messages.append({
                "role": "assistant",
                "content": None,
                "function_call": {
                    "name": function_name,
                    "arguments": response_message.function_call.arguments
                }
            })
            
            messages.append({
                "role": "function",
                "name": function_name,
                "content": json.dumps(function_result)
            })
            
            # Get final response from AI
            final_response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=800,
                temperature=0.7
            )
            
            ai_response = final_response.choices[0].message.content.strip()
        else:
            # No function call needed
            ai_response = response_message.content.strip()
        
        return jsonify({
            "response": ai_response,
            "status": "success"
        }), 200
        
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return jsonify({
            "response": "I'm sorry, I'm having trouble processing your request right now. Please try again later.",
            "status": "error"
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 