import React, { useState, useEffect } from 'react';
import { StudentsResponse, User } from '../types';

interface StudentsListProps {
  currentUser: User;
}

const StudentsList: React.FC<StudentsListProps> = ({ currentUser }) => {
  const [students, setStudents] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newStudent, setNewStudent] = useState({ name: '', email: '', student_id: '' });

  const API_BASE = process.env.NODE_ENV === 'development' ? '' : 'http://localhost:5001';

  useEffect(() => {
    fetchStudents();
  }, []);

  const fetchStudents = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/api/students`, {
        credentials: 'include',
      });
      if (!response.ok) {
        throw new Error('Failed to fetch students');
      }
      const data: StudentsResponse = await response.json();
      setStudents(data.students);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleAddStudent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newStudent.name || !newStudent.email || !newStudent.student_id) {
      setError('All fields are required');
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/api/users`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          ...newStudent,
          role: 'student'
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to add student');
      }

      // Reset form and refresh list
      setNewStudent({ name: '', email: '', student_id: '' });
      fetchStudents();
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add student');
    }
  };

  return (
    <div className="tab-content">
      <div className="content-area">
        {currentUser.role === 'admin' && (
          <div className="add-student-section">
            <h3>Add New Student</h3>
            <form onSubmit={handleAddStudent} className="user-form">
              <input
                type="text"
                placeholder="Student Name"
                value={newStudent.name}
                onChange={(e) => setNewStudent({ ...newStudent, name: e.target.value })}
                required
              />
              <input
                type="email"
                placeholder="Email"
                value={newStudent.email}
                onChange={(e) => setNewStudent({ ...newStudent, email: e.target.value })}
                required
              />
              <input
                type="text"
                placeholder="Student ID"
                value={newStudent.student_id}
                onChange={(e) => setNewStudent({ ...newStudent, student_id: e.target.value })}
                required
              />
              <button type="submit">Add Student</button>
            </form>
            {error && <div className="error-message">{error}</div>}
          </div>
        )}

        <div className="students-section">
          <h3>Enrolled Students ({students.length})</h3>
          {loading ? (
            <div className="loading-state">Loading students...</div>
          ) : error && currentUser.role !== 'admin' ? (
            <div className="error-state">{error}</div>
          ) : (
            <div className="students-grid">
              {students.map((student) => (
                <div key={student.id} className="student-card">
                  <h4>{student.name}</h4>
                  <p>{student.email}</p>
                  <div className="student-stats">
                    <span className="student-id">{student.student_id}</span>
                    <span className="attendance-status">Enrolled</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StudentsList; 