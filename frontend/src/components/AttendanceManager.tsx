import React, { useState, useEffect } from 'react';
import { useTheme } from '../contexts/ThemeContext';
import { AttendanceRow, Class, User } from '../types';

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
  const [bulkStatus, setBulkStatusSelection] = useState('present');

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
      const data: AttendanceRow[] = await response.json();
      
      // Check if attendance is verified for this date
      const verified = Array.isArray(data) && data.some(row => row.id);
      setIsVerified(verified);
      
      // If not verified, set all students to '-' (unknown) by default
      if (!verified) {
        const defaultAttendance = data.map(row => ({
          ...row,
          status: row.status || '-'
        }));
        setAttendance(defaultAttendance);
      } else {
        setAttendance(data);
      }
      
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const toggleAttendanceStatus = (studentId: number) => {
    const statusCycle = ['present', 'absent', 'tardy', 'excused', '-'];
    
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

  const setBulkStatus = async () => {
    setAttendance(prev => prev.map(row => ({
      ...row,
      status: bulkStatus
    })));
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
    // If clicking the same student, unselect them
    if (selectedStudent?.student_id === student.student_id) {
      setSelectedStudent(null);
    } else {
      setSelectedStudent(student);
    }
  };

  const getStatusDisplay = (status: string) => {
    switch (status) {
      case 'present':
        return { letter: 'P', color: theme.statusPresent, className: 'status-present' };
      case 'absent':
        return { letter: 'A', color: theme.statusAbsent, className: 'status-absent' };
      case 'tardy':
        return { letter: 'T', color: theme.statusTardy, className: 'status-tardy' };
      case 'excused':
        return { letter: 'E', color: theme.statusExcused, className: 'status-excused' };
      case '-':
        return { letter: '-', color: theme.statusUnset, className: 'status-unknown' };
      default:
        return { letter: '-', color: theme.statusUnset, className: 'status-unknown' };
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
            <div className="bulk-status-controls">
              <button 
                className="bulk-status-button"
                onClick={setBulkStatus}
                title="Apply selected status to all students"
              >
                Set All To:
              </button>
              <select 
                className="bulk-status-select"
                value={bulkStatus}
                onChange={(e) => setBulkStatusSelection(e.target.value)}
              >
                <option value="present">Present</option>
                <option value="absent">Absent</option>
                <option value="tardy">Tardy</option>
                <option value="excused">Excused</option>
                <option value="-">Unknown (-)</option>
              </select>
            </div>
            <button 
              className={`verify-button ${isVerified ? 'verified' : ''}`}
              onClick={verifyAttendance}
              disabled={isVerified || isVerifying}
            >
              {isVerifying ? 'Saving...' : isVerified ? 'Active' : 'Save Initial'}
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
                    </tr>
                  </thead>
                  <tbody>
                    {attendance.map((row) => {
                      const statusDisplay = getStatusDisplay(row.status);
                      const isSelected = selectedStudent?.student_id === row.student_id;
                      return (
                        <tr 
                          key={row.student_id}
                          className={`attendance-row ${isSelected ? 'selected' : ''}`}
                        >
                          <td 
                            className="name-cell clickable"
                            onClick={() => handleStudentInfoClick(row)}
                            title="Click to view student info"
                          >
                            {row.name}
                          </td>
                          <td 
                            className="status-cell clickable"
                            onClick={() => toggleAttendanceStatus(row.student_id)}
                            title="Click to change status"
                          >
                            <span 
                              className={`status-letter ${statusDisplay.className}`}
                            >
                              {statusDisplay.letter}
                            </span>
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
              ) : (
                <div className="no-student-selected">
                  <p>Click on a student name to view their information</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AttendanceManager; 