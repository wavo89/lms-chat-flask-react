import React, { useState, useEffect } from 'react';
import './Dashboard.css';
import { useTheme } from '../contexts/ThemeContext';

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
  class_id?: number;
  class_name?: string;
  attendance: AttendanceRow[];
  count: number;
}

interface Class {
  id: number;
  name: string;
  description?: string;
  teacher_id: number;
  teacher_name?: string;
  student_count: number;
  is_active: boolean;
}

interface Assignment {
  id: number;
  name: string;
  description?: string;
  class_id: number;
  class_name?: string;
  max_points: number;
  due_date?: string;
  assignment_type: string;
}

interface Grade {
  id: number;
  student_id: number;
  assignment_id: number;
  student_name?: string;
  student_student_id?: string;
  assignment_name?: string;
  assignment_max_points?: number;
  points_earned?: number;
  percentage?: number;
  letter_grade?: string;
  comments?: string;
}

interface GradesResponse {
  class: Class;
  assignments: Assignment[];
  students: Array<{
    id: number;
    name: string;
    student_id: string;
    grades: { [assignment_id: number]: Grade };
  }>;
  grades: { [student_id: number]: { [assignment_id: number]: Grade } };
}

interface DashboardProps {
  currentUser: User;
  onLogout: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ currentUser, onLogout }) => {
  const { theme, isDark, toggleTheme } = useTheme();
  const [activeTab, setActiveTab] = useState('attendance');
  const [students, setStudents] = useState<User[]>([]);
  const [attendance, setAttendance] = useState<AttendanceRow[]>([]);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newStudent, setNewStudent] = useState({ name: '', email: '', student_id: '' });
  const [selectedStudent, setSelectedStudent] = useState<AttendanceRow | null>(null);
  const [isVerified, setIsVerified] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);
  const [classes, setClasses] = useState<Class[]>([]);
  const [selectedClass, setSelectedClass] = useState<number | null>(null);
  const [selectedGradeClass, setSelectedGradeClass] = useState<number | null>(null);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [gradesData, setGradesData] = useState<GradesResponse | null>(null);
  const [loadingGrades, setLoadingGrades] = useState(false);

  const API_BASE = process.env.NODE_ENV === 'development' ? '' : 'http://localhost:5001';
  const isTeacher = currentUser.role === 'teacher' || currentUser.role === 'admin';

  useEffect(() => {
    if (activeTab === 'attendance') {
      if (isTeacher) {
        setIsVerified(false); // Reset verification status when date/class changes
        fetchAttendance();
      } else {
        fetchStudents();
      }
    }
  }, [activeTab, selectedDate, selectedClass, isTeacher]);

  useEffect(() => {
    // Fetch classes when component mounts
    fetchClasses();
  }, []);

  useEffect(() => {
    // Fetch grades when grade class changes
    if (selectedGradeClass) {
      fetchGrades(selectedGradeClass);
    } else {
      setGradesData(null);
    }
  }, [selectedGradeClass]);

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

  const fetchClasses = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/classes`, {
        credentials: 'include',
      });
      if (!response.ok) {
        throw new Error('Failed to fetch classes');
      }
      const data: Class[] = await response.json();
      setClasses(data);
    } catch (err) {
      console.error('Error fetching classes:', err);
    }
  };

  const fetchGrades = async (classId: number) => {
    try {
      setLoadingGrades(true);
      const response = await fetch(`${API_BASE}/api/classes/${classId}/grades`, {
        credentials: 'include',
      });
      if (!response.ok) {
        throw new Error('Failed to fetch grades');
      }
      const data: GradesResponse = await response.json();
      setGradesData(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch grades');
      setGradesData(null);
    } finally {
      setLoadingGrades(false);
    }
  };

  const updateGrade = async (gradeId: number, pointsEarned: number | null) => {
    try {
      const response = await fetch(`${API_BASE}/api/grades/${gradeId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          points_earned: pointsEarned
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to update grade');
      }

      // Refresh grades data
      if (selectedGradeClass) {
        await fetchGrades(selectedGradeClass);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update grade');
    }
  };

  const fetchAttendance = async () => {
    try {
      setLoading(true);
      const classParam = selectedClass ? `&class_id=${selectedClass}` : '';
      const response = await fetch(`${API_BASE}/api/attendance?date=${selectedDate}${classParam}`, {
        credentials: 'include',
      });
      if (!response.ok) {
        throw new Error('Failed to fetch attendance');
      }
      const data: AttendanceResponse = await response.json();
      
      // Check if attendance is verified for this date
      const verified = data.attendance.some(row => row.record_id);
      setIsVerified(verified);
      
      // If not verified, set all students to 'present' by default
      if (!verified) {
        const attendanceWithDefaults = data.attendance.map(row => ({
          ...row,
          status: 'present'
        }));
        setAttendance(attendanceWithDefaults);
      } else {
        setAttendance(data.attendance);
      }
      
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const toggleAttendanceStatus = async (studentId: number) => {
    const currentRow = attendance.find(row => row.student_id === studentId);
    if (!currentRow) return;

    // Cycle through statuses: present -> absent -> tardy -> excused -> present
    const statusCycle = ['present', 'absent', 'tardy', 'excused'];
    const currentIndex = statusCycle.indexOf(currentRow.status);
    // If status is not found (empty/undefined), start at -1 so next will be 0 (present)
    const nextIndex = currentIndex === -1 ? 0 : (currentIndex + 1) % statusCycle.length;
    const nextStatus = statusCycle[nextIndex];

    // Update local state immediately
    setAttendance(prev => 
      prev.map(row => 
        row.student_id === studentId 
          ? { ...row, status: nextStatus } 
          : row
      )
    );

    // Auto-save to backend only if already verified
    if (isVerified) {
      try {
        const response = await fetch(`${API_BASE}/api/attendance`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({
            date: selectedDate,
            records: [{
              student_id: studentId,
              status: nextStatus
            }]
          }),
        });

        if (!response.ok) {
          throw new Error('Failed to save attendance');
        }
      } catch (err) {
        console.error('Error saving attendance:', err);
        // Revert the change if save failed
        setAttendance(prev => 
          prev.map(row => 
            row.student_id === studentId 
              ? { ...row, status: currentRow.status } 
              : row
          )
        );
      }
    }
  };

  const verifyAttendance = async () => {
    try {
      setIsVerifying(true);
      const records = attendance.map(row => ({
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
          class_id: selectedClass,
          records: records
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to verify attendance');
      }

      setIsVerified(true);
      // Refresh attendance to get record IDs
      fetchAttendance();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to verify attendance');
    } finally {
      setIsVerifying(false);
    }
  };

  const handleStudentInfoClick = (student: AttendanceRow) => {
    setSelectedStudent(student);
  };

  const getStatusDisplay = (status: string) => {
    switch (status) {
      case 'present': return { letter: 'P', color: theme.statusPresent };
      case 'absent': return { letter: 'A', color: theme.statusAbsent };
      case 'tardy': return { letter: 'T', color: theme.statusTardy };
      case 'excused': return { letter: 'E', color: theme.statusExcused };
      default: return { letter: '-', color: theme.statusUnset };
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
              <div className="secondary-nav">
                <div className="secondary-nav-inner">
                  <h2>Daily Attendance</h2>
                  <div className="nav-controls">
                    <div className="class-selector">
                      <select
                        value={selectedClass || ''}
                        onChange={(e) => setSelectedClass(e.target.value ? parseInt(e.target.value) : null)}
                      >
                        <option value="">All Students</option>
                        {classes.map(cls => (
                          <option key={cls.id} value={cls.id}>
                            {cls.name}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="date-selector">
                      <input
                        type="date"
                        id="attendance-date"
                        value={selectedDate}
                        onChange={(e) => setSelectedDate(e.target.value)}
                      />
                    </div>
                    <button 
                      className={`verify-button ${isVerified ? 'verified' : ''}`}
                      onClick={verifyAttendance}
                      disabled={isVerified || isVerifying}
                    >
                      {isVerifying ? 'Verifying...' : isVerified ? 'Verified ✓' : 'Verify'}
                    </button>
                  </div>
                </div>
              </div>

              <div className="content-area">
                <div className="attendance-layout">
                  <div className="attendance-table-section">
                  {loading ? (
                    <div className="loading-state">Loading attendance...</div>
                  ) : error ? (
                    <div className="error-state">Error: {error}</div>
                  ) : (
                    <div className="attendance-table-container">
                      <table className="attendance-table">
                        <thead>
                          <tr>
                            <th>Name</th>
                            <th>Status</th>
                            <th>Info</th>
                          </tr>
                        </thead>
                        <tbody>
                          {attendance.map((row) => {
                            const statusDisplay = getStatusDisplay(row.status);
                            return (
                              <tr 
                                key={row.student_id}
                                className="attendance-row"
                                onClick={() => toggleAttendanceStatus(row.student_id)}
                              >
                                <td className="name-cell">
                                  {row.name}
                                </td>
                                <td className="status-cell">
                                  <span 
                                    className="status-letter"
                                    style={{ color: statusDisplay.color }}
                                  >
                                    {statusDisplay.letter}
                                  </span>
                                </td>
                                <td className="info-cell">
                                  <button 
                                    className="info-button"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleStudentInfoClick(row);
                                    }}
                                    title="View student info"
                                  >
                                    <span className="info-icon">ⓘ</span>
                                  </button>
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>

                <div className="student-info-panel">
                  <div className="info-panel-header">
                    <h3>Student Information</h3>
                  </div>
                  <div className="info-panel-content">
                    {selectedStudent ? (
                      <div className="student-details">
                        <div className="detail-item">
                          <label>Name:</label>
                          <span>{selectedStudent.name}</span>
                        </div>
                        <div className="detail-item">
                          <label>Student ID:</label>
                          <span>{selectedStudent.student_student_id}</span>
                        </div>
                        <div className="detail-item">
                          <label>Email:</label>
                          <span>{selectedStudent.email}</span>
                        </div>
                      </div>
                    ) : (
                      <div className="no-student-selected">
                        <p>No student selected</p>
                        <small>Click the info button (ⓘ) next to a student to view their details</small>
                      </div>
                    )}
                  </div>
                </div>
              </div>
              </div>
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
            <div className="secondary-nav">
              <div className="secondary-nav-inner">
                <h2>Student Grades</h2>
                <div className="nav-controls">
                  <div className="class-selector">
                    <select
                      value={selectedGradeClass || ''}
                      onChange={(e) => setSelectedGradeClass(e.target.value ? parseInt(e.target.value) : null)}
                    >
                      <option value="">Select a Class</option>
                      {classes.map(cls => (
                        <option key={cls.id} value={cls.id}>
                          {cls.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            </div>
            <div className="content-area">
              {selectedGradeClass ? (
                <div className="grades-container">
                  {loadingGrades ? (
                    <div className="loading-state">Loading grades...</div>
                  ) : gradesData ? (
                    <div className="grades-table-container">
                      <table className="grades-table">
                        <thead>
                          <tr>
                            <th className="student-name-header">Student</th>
                            {gradesData.assignments.map(assignment => (
                              <th key={assignment.id} className="assignment-header">
                                <div className="assignment-header-content">
                                  <div className="assignment-name">{assignment.name}</div>
                                  <div className="assignment-points">({assignment.max_points} pts)</div>
                                </div>
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {gradesData.students.map(student => (
                            <tr key={student.id} className="grade-row">
                              <td className="student-name-cell">{student.name}</td>
                              {gradesData.assignments.map(assignment => {
                                const grade = student.grades[assignment.id];
                                return (
                                  <td key={assignment.id} className="grade-cell">
                                    <input
                                      type="number"
                                      min="0"
                                      max={assignment.max_points}
                                      step="0.1"
                                      value={grade?.points_earned ?? ''}
                                      onChange={(e) => {
                                        const value = e.target.value === '' ? null : parseFloat(e.target.value);
                                        if (grade?.id) {
                                          updateGrade(grade.id, value);
                                        }
                                      }}
                                      className="grade-input"
                                      placeholder="-"
                                    />
                                  </td>
                                );
                              })}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="error-state">
                      {error || 'No grades data available'}
                    </div>
                  )}
                </div>
              ) : (
                <div className="grades-placeholder">
                  <div className="placeholder-content">
                    <h3>📊 Grades Management</h3>
                    <p>Please select a class above to view and manage grades.</p>
                  </div>
                </div>
              )}
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
          <h1>LMS</h1>
        </div>
                  <div className="header-actions">
            <button onClick={toggleTheme} className="theme-toggle-button">
              {isDark ? '🌙' : '☀️'}
            </button>
          <button onClick={onLogout} className="logout-button">
            Logout
          </button>
        </div>
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

      <div className="dashboard-main">
        {renderTabContent()}
      </div>
    </div>
  );
};

export default Dashboard; 