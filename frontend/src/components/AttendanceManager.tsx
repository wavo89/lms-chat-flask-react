import React, { useState, useEffect } from 'react';
import { useTheme } from '../contexts/ThemeContext';
import { AttendanceRow, AttendanceResponse, Class, User } from '../types';

interface AttendanceManagerProps {
  currentUser: User;
  classes: Class[];
}

const AttendanceManager: React.FC<AttendanceManagerProps> = ({ currentUser, classes }) => {
  const { theme } = useTheme();
  const [attendance, setAttendance] = useState<AttendanceRow[]>([]);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [selectedClass, setSelectedClass] = useState<number | null>(null);
  const [selectedStudent, setSelectedStudent] = useState<AttendanceRow | null>(null);
  const [isVerified, setIsVerified] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const API_BASE = process.env.NODE_ENV === 'development' ? '' : 'http://localhost:5001';

  useEffect(() => {
    setIsVerified(false); // Reset verification status when date/class changes
    fetchAttendance();
  }, [selectedDate, selectedClass]);

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
        const defaultAttendance = data.attendance.map(row => ({
          ...row,
          status: row.status || 'present'
        }));
        setAttendance(defaultAttendance);
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

  const toggleAttendanceStatus = (studentId: number) => {
    const statusCycle = ['present', 'absent', 'tardy', 'excused'];
    
    setAttendance(prev => prev.map(row => {
      if (row.student_id === studentId) {
        const currentIndex = statusCycle.indexOf(row.status);
        const nextIndex = currentIndex === -1 ? 0 : (currentIndex + 1) % statusCycle.length;
        const newStatus = statusCycle[nextIndex];
        
        // Only auto-save if already verified
        if (isVerified) {
          // Auto-save logic would go here if needed
        }
        
        return { ...row, status: newStatus };
      }
      return row;
    }));
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
      case 'present':
        return { letter: 'P', color: theme.statusPresent };
      case 'absent':
        return { letter: 'A', color: theme.statusAbsent };
      case 'tardy':
        return { letter: 'T', color: theme.statusTardy };
      case 'excused':
        return { letter: 'E', color: theme.statusExcused };
      default:
        return { letter: '-', color: theme.statusUnset };
    }
  };

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
              <div className="error-state">{error}</div>
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

          {selectedStudent && (
            <div className="student-info-panel">
              <div className="info-panel-header">
                <h3>Student Information</h3>
              </div>
              <div className="info-panel-content">
                <div className="student-details">
                  <div className="detail-item">
                    <label>Name</label>
                    <span>{selectedStudent.name}</span>
                  </div>
                  <div className="detail-item">
                    <label>Student ID</label>
                    <span>{selectedStudent.student_student_id}</span>
                  </div>
                  <div className="detail-item">
                    <label>Email</label>
                    <span>{selectedStudent.email}</span>
                  </div>
                </div>
                <button 
                  className="close-panel-button"
                  onClick={() => setSelectedStudent(null)}
                >
                  Close
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AttendanceManager; 