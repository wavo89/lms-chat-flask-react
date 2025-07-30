import React, { useState, useEffect } from 'react';
import './Dashboard.css';

interface User {
  id: number;
  name: string;
  email: string;
  role: string;
  student_id?: string;
  created_at?: string;
  updated_at?: string;
  is_active?: boolean;
}

interface StudentsResponse {
  students: User[];
  count: number;
}

interface DashboardProps {
  currentUser: User;
  onLogout: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ currentUser, onLogout }) => {
  const [activeTab, setActiveTab] = useState('attendance');
  const [students, setStudents] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newStudent, setNewStudent] = useState({ name: '', email: '', student_id: '' });

  const API_BASE = process.env.NODE_ENV === 'development' ? '' : 'http://localhost:5001';

  useEffect(() => {
    if (activeTab === 'attendance') {
      fetchStudents();
    }
  }, [activeTab]);

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
    if (!newStudent.name || !newStudent.email || !newStudent.student_id) return;

    try {
      const response = await fetch(`${API_BASE}/api/users`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          name: newStudent.name,
          email: newStudent.email,
          role: 'student',
          student_id: newStudent.student_id
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to add student');
      }

      setNewStudent({ name: '', email: '', student_id: '' });
      fetchStudents();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add student');
    }
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'attendance':
        return (
          <div className="tab-content">
            <div className="content-header">
              <h2>Student Attendance</h2>
              <p>Manage student enrollment and attendance tracking</p>
            </div>

            <div className="add-user-section">
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
                  placeholder="Student Email"
                  value={newStudent.email}
                  onChange={(e) => setNewStudent({ ...newStudent, email: e.target.value })}
                  required
                />
                <input
                  type="text"
                  placeholder="Student ID (e.g., STU011)"
                  value={newStudent.student_id}
                  onChange={(e) => setNewStudent({ ...newStudent, student_id: e.target.value })}
                  required
                />
                <button type="submit">Add Student</button>
              </form>
            </div>

            {loading ? (
              <div className="loading-state">Loading students...</div>
            ) : error ? (
              <div className="error-state">Error: {error}</div>
            ) : (
              <div className="students-section">
                <h3>Enrolled Students ({students.length})</h3>
                <div className="students-grid">
                  {students.map((student: User) => (
                    <div key={student.id} className="student-card">
                      <h4>{student.name}</h4>
                      <p>{student.email}</p>
                      <div className="student-stats">
                        <span className="student-id">{student.student_id}</span>
                        <span className="attendance-status">Present</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        );

      case 'grades':
        return (
          <div className="tab-content">
            <div className="content-header">
              <h2>Student Grades</h2>
              <p>Track and manage student performance and grades</p>
            </div>
            <div className="grades-placeholder">
              <div className="placeholder-content">
                <h3>📊 Grades Management</h3>
                <p>Grade tracking functionality coming soon...</p>
                <div className="placeholder-features">
                  <div className="feature-item">📝 Assignment Grades</div>
                  <div className="feature-item">📈 Progress Tracking</div>
                  <div className="feature-item">📋 Report Cards</div>
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div className="header-content">
          <h1>LMS Dashboard</h1>
          <p>Welcome back, {currentUser.name}!</p>
        </div>
        <button onClick={onLogout} className="logout-button">
          Logout
        </button>
      </div>

      <div className="dashboard-navigation">
        <div className="nav-tabs">
          <button
            className={`nav-tab ${activeTab === 'attendance' ? 'active' : ''}`}
            onClick={() => setActiveTab('attendance')}
          >
            📋 Attendance
          </button>
          <button
            className={`nav-tab ${activeTab === 'grades' ? 'active' : ''}`}
            onClick={() => setActiveTab('grades')}
          >
            📊 Grades
          </button>
        </div>
      </div>

      <div className="dashboard-content">
        {renderTabContent()}
      </div>
    </div>
  );
};

export default Dashboard; 