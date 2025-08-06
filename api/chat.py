from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from models import db, ChatHistory, User, AttendanceRecord
from .utils import teacher_required
import os
import json
import requests
from openai import OpenAI

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
@login_required
def chat_with_ai():
    """Chat with AI assistant."""
    try:
        # Initialize OpenAI client (lazy loading to avoid import-time env var issues)
        openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        data = request.get_json()
        if not data or not data.get('message'):
            return jsonify({"error": "Message is required"}), 400
        
        user_message = data['message']
        user_name = current_user.name
        user_role = current_user.role
        
        # AI function definitions for attendance data access
        available_functions = [
            {
                "name": "get_attendance_summary",
                "description": "Get attendance summary for recent days with statistics",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": "Number of recent weekdays to analyze (default: 7)"
                        }
                    }
                }
            },
            {
                "name": "get_student_attendance",
                "description": "Get detailed attendance history for a specific student",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "student_name": {
                            "type": "string",
                            "description": "Name of the student to look up"
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of recent days to include (default: 14)"
                        }
                    },
                    "required": ["student_name"]
                }
            }
        ]
        
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
        
        # Save chat history to database
        try:
            chat_record = ChatHistory(
                user_id=current_user.id,
                message=user_message,
                response=ai_response,
                session_id=data.get('session_id')
            )
            db.session.add(chat_record)
            db.session.commit()
        except Exception as e:
            print(f"Error saving chat history: {e}")
        
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

@chat_bp.route('/chat-history', methods=['GET'])
@login_required
def get_chat_history():
    """Get chat history for teachers (all students) or current user."""
    try:
        if current_user.role in ['teacher', 'admin']:
            student_id = request.args.get('student_id', type=int)
            if student_id:
                chats = ChatHistory.query.filter_by(user_id=student_id).order_by(ChatHistory.timestamp.desc()).limit(50).all()
            else:
                chats = ChatHistory.query.join(User).filter(User.role == 'student').order_by(ChatHistory.timestamp.desc()).limit(100).all()
        else:
            chats = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.timestamp.desc()).limit(50).all()
        
        return jsonify([chat.to_dict() for chat in chats]), 200
    except Exception as e:
        print(f"Error fetching chat history: {e}")
        return jsonify({"error": "Failed to fetch chat history"}), 500

@chat_bp.route('/chat-history/<int:chat_id>', methods=['DELETE'])
@login_required
@teacher_required
def delete_chat_history(chat_id):
    """Delete a specific chat history record (teachers only)."""
    try:
        chat = ChatHistory.query.get(chat_id)
        if not chat:
            return jsonify({"error": "Chat history not found"}), 404
        
        db.session.delete(chat)
        db.session.commit()
        return jsonify({"message": "Chat history deleted"}), 200
    except Exception as e:
        print(f"Error deleting chat history: {e}")
        return jsonify({"error": "Failed to delete chat history"}), 500

# AI-specific endpoints for function calling
@chat_bp.route('/ai/attendance-summary', methods=['GET'])
@login_required
def ai_attendance_summary():
    """Get attendance summary for AI assistant - recent days with statistics."""
    try:
        from datetime import timedelta
        
        days = request.args.get('days', 7, type=int)
        
        # Calculate date range (last N weekdays)
        end_date = datetime.now().date()
        current_date = end_date
        dates = []
        
        while len(dates) < days:
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                dates.append(current_date)
            current_date = current_date - timedelta(days=1)
        
        dates.reverse()  # Chronological order
        
        # Get attendance data for these dates
        summary = {
            "period": f"Last {days} weekdays",
            "start_date": dates[0].isoformat(),
            "end_date": dates[-1].isoformat(),
            "daily_stats": [],
            "student_issues": []
        }
        
        students = User.query.filter_by(role='student').all()
        student_attendance = {s.id: {"name": s.name, "absences": 0, "tardies": 0, "days": len(dates)} for s in students}
        
        for attendance_date in dates:
            records = AttendanceRecord.query.filter_by(date=attendance_date).all()
            records_dict = {r.student_id: r.status for r in records}
            
            day_stats = {
                "date": attendance_date.isoformat(),
                "present": 0,
                "absent": 0,
                "tardy": 0,
                "excused": 0,
                "total_students": len(students)
            }
            
            for student in students:
                status = records_dict.get(student.id, 'present')
                day_stats[status] += 1
                
                # Track individual student patterns
                if status == 'absent':
                    student_attendance[student.id]["absences"] += 1
                elif status == 'tardy':
                    student_attendance[student.id]["tardies"] += 1
            
            summary["daily_stats"].append(day_stats)
        
        # Identify students with attendance issues
        for student_id, data in student_attendance.items():
            absence_rate = data["absences"] / data["days"]
            tardy_rate = data["tardies"] / data["days"]
            
            if absence_rate >= 0.3 or tardy_rate >= 0.4:  # 30% absent or 40% tardy
                summary["student_issues"].append({
                    "name": data["name"],
                    "absences": data["absences"],
                    "tardies": data["tardies"],
                    "absence_rate": round(absence_rate * 100, 1),
                    "tardy_rate": round(tardy_rate * 100, 1)
                })
        
        return jsonify(summary), 200
    except Exception as e:
        print(f"Error generating attendance summary: {e}")
        return jsonify({"error": "Failed to generate attendance summary"}), 500

@chat_bp.route('/ai/student-attendance/<int:student_id>', methods=['GET'])
@login_required
def ai_student_attendance(student_id):
    """Get detailed attendance for a specific student."""
    try:
        from datetime import timedelta
        
        student = User.query.get(student_id)
        if not student or student.role != 'student':
            return jsonify({"error": "Student not found"}), 404
        
        days = request.args.get('days', 14, type=int)
        
        # Get recent attendance records
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        records = AttendanceRecord.query.filter(
            AttendanceRecord.student_id == student_id,
            AttendanceRecord.date >= start_date,
            AttendanceRecord.date <= end_date
        ).order_by(AttendanceRecord.date.desc()).all()
        
        summary = {
            "student": {
                "name": student.name,
                "student_id": student.student_id
            },
            "period": f"Last {days} days",
            "records": [r.to_dict() for r in records],
            "statistics": {
                "total_days": len(records),
                "present": len([r for r in records if r.status == 'present']),
                "absent": len([r for r in records if r.status == 'absent']),
                "tardy": len([r for r in records if r.status == 'tardy']),
                "excused": len([r for r in records if r.status == 'excused'])
            }
        }
        
        return jsonify(summary), 200
    except Exception as e:
        print(f"Error getting student attendance: {e}")
        return jsonify({"error": "Failed to get student attendance"}), 500 