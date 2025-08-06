from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date
from models import db, AttendanceRecord, User, Class
from .utils import teacher_required

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/attendance', methods=['GET'])
@login_required
def get_attendance():
    """Get attendance records."""
    try:
        attendance_date = request.args.get('date', date.today().isoformat())
        class_id = request.args.get('class_id', type=int)
        
        attendance_date_obj = datetime.strptime(attendance_date, '%Y-%m-%d').date()
        
        if class_id:
            class_obj = Class.query.get(class_id)
            if not class_obj:
                return jsonify({"error": "Class not found"}), 404
            
            students = class_obj.students
            records = AttendanceRecord.query.filter_by(
                date=attendance_date_obj,
                class_id=class_id
            ).all()
        else:
            students = User.query.filter_by(role='student').all()
            records = AttendanceRecord.query.filter_by(
                date=attendance_date_obj,
                class_id=None
            ).all()
        
        records_dict = {record.student_id: record for record in records}
        
        attendance_data = []
        for student in students:
            record = records_dict.get(student.id)
            attendance_data.append({
                'id': record.id if record else None,
                'student_id': student.id,
                'student_name': student.name,
                'student_student_id': student.student_id,
                'date': attendance_date,
                'status': record.status if record else 'present',
                'class_id': class_id
            })
        
        return jsonify(attendance_data), 200
    except Exception as e:
        print(f"Error fetching attendance: {e}")
        return jsonify({"error": "Failed to fetch attendance"}), 500

@attendance_bp.route('/attendance', methods=['POST'])
@login_required
@teacher_required
def update_attendance():
    """Update attendance records."""
    try:
        data = request.get_json()
        attendance_date = data.get('date', date.today().isoformat())
        class_id = data.get('class_id')
        records = data.get('records', [])
        
        attendance_date_obj = datetime.strptime(attendance_date, '%Y-%m-%d').date()
        
        for record_data in records:
            student_id = record_data['student_id']
            status = record_data['status']
            
            existing_record = AttendanceRecord.query.filter_by(
                student_id=student_id,
                date=attendance_date_obj,
                class_id=class_id
            ).first()
            
            if existing_record:
                existing_record.status = status
                existing_record.updated_at = datetime.utcnow()
            else:
                new_record = AttendanceRecord(
                    date=attendance_date_obj,
                    status=status,
                    student_id=student_id,
                    teacher_id=current_user.id,
                    class_id=class_id
                )
                db.session.add(new_record)
        
        db.session.commit()
        return jsonify({"message": "Attendance updated successfully"}), 200
    except Exception as e:
        print(f"Error updating attendance: {e}")
        return jsonify({"error": "Failed to update attendance"}), 500 