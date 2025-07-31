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

interface AttendanceRow {
  student_id: number;
  student_student_id: string;
  name: string;
  email: string;
  status: string;
  record_id?: number;
}

interface AttendanceResponse {
  date: string;
  attendance: AttendanceRow[];
  count: number;
}

interface DashboardProps {
  currentUser: User;
  onLogout: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ currentUser, onLogout }) => {
  const [activeTab, setActiveTab] = useState('attendance');
  const [students, setStudents] = useState<User[]>([]);
  const [attendance, setAttendance] = useState<AttendanceRow[]>([]);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newStudent, setNewStudent] = useState({ name: '', email: '', student_id: '' });
  const [saving, setSaving] = useState(false);

  const API_BASE = process.env.NODE_ENV === 'development' ? '' : 'http://localhost:5001';
  const isTeacher = currentUser.role === 'teacher' || currentUser.role === 'admin';

  useEffect(() => {
    if (activeTab === 'attendance') {
      if (isTeacher) {
        fetchAttendance();
      } else {
        fetchStudents();
      }
    }
  }, [activeTab, selectedDate, isTeacher]);

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

  const fetchAttendance = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/api/attendance?date=${selectedDate}`, {
        credentials: 'include',
      });
      if (!response.ok) {
        throw new Error('Failed to fetch attendance');
      }
      const data: AttendanceResponse = await response.json();
      setAttendance(data.attendance);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleAttendanceChange = (studentId: number, status: string) => {
    setAttendance(prev => 
      prev.map(row => 
        row.student_id === studentId 
          ? { ...row, status } 
          : row
      )
    );
  };

  const saveAttendance = async () => {
    try {
      setSaving(true);
      const records = attendance
        .filter(row => row.status) // Only save rows with status
        .map(row => ({
          student_id: row.student_id,
          status: row.status
        }));

      const response = await fetch(`${API_BASE}/api/attendance`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          date: selectedDate,
          records: records
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to save attendance');
      }

      const result = await response.json();
      alert(`Saved ${result.saved_count} attendance records!`);
      fetchAttendance(); // Refresh data
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save attendance');
    } finally {
      setSaving(false);
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
        if (isTeacher) {
          return (
            <div className="tab-content">
              <div className="content-header">
                <h2>Daily Attendance</h2>
                <p>Mark student attendance for the selected date</p>
              </div>

              <div className="attendance-controls">
                <div className="date-selector">
                  <label htmlFor="attendance-date">Date:</label>
                  <input
                    type="date"
                    id="attendance-date"
                    value={selectedDate}
                    onChange={(e) => setSelectedDate(e.target.value)}
                  />
                </div>
                <button 
                  onClick={saveAttendance} 
                  disabled={saving}
                  className="save-attendance-button"
                >
                  {saving ? 'Saving...' : 'Save Attendance'}
                </button>
              </div>

              {loading ? (
                <div className="loading-state">Loading attendance...</div>
              ) : error ? (
                <div className="error-state">Error: {error}</div>
              ) : (
                <div className="attendance-table-container">
                  <table className="attendance-table">
                    <thead>
                      <tr>
                        <th>Student ID</th>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {attendance.map((row) => (
                        <tr key={row.student_id}>
                          <td>{row.student_student_id}</td>
                          <td>{row.name}</td>
                          <td>{row.email}</td>
                          <td>
                            <select
                              value={row.status}
                              onChange={(e) => handleAttendanceChange(row.student_id, e.target.value)}
                              className="status-select"
                            >
                              <option value="">Select...</option>
                              <option value="present">Present</option>
                              <option value="absent">Absent</option>
                              <option value="tardy">Tardy</option>
                              <option value="excused">Excused</option>
                            </select>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          );
        } else {
          return (
            <div className="tab-content">
              <div className="content-header">
                <h2>Student Enrollment</h2>
                <p>Manage student enrollment and view student list</p>
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
                          <span className="attendance-status">Enrolled</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        }

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