from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
from openai import OpenAI
from config import Config
from models import db, bcrypt, User

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

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Message is required"}), 400
    
    user_message = data['message']
    user_name = data.get('user', current_user.name)
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": f"You are a helpful AI assistant for a Learning Management System (LMS). You're helping {user_name}, a user of the system. Be friendly, helpful, and focus on educational topics, course management, student progress, and learning-related questions. Keep responses concise but informative."
                },
                {
                    "role": "user", 
                    "content": user_message
                }
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content.strip()
        
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