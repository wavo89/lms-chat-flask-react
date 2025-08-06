import React, { useState, useEffect } from 'react';
import { User, Class } from '../types';

interface ClassDetails extends Class {
  teacher_name?: string;
  student_count: number;
  students?: User[];
}

interface ClassroomManagerProps {
  currentUser: User;
  classes: Class[];
  onClassesUpdate: () => void;
}

const ClassroomManager: React.FC<ClassroomManagerProps> = ({ currentUser, classes, onClassesUpdate }) => {
  const [classDetails, setClassDetails] = useState<ClassDetails[]>([]);
  const [students, setStudents] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedClass, setSelectedClass] = useState<ClassDetails | null>(null);
  const [showEnrollmentManager, setShowEnrollmentManager] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    is_active: true
  });

  const API_BASE = process.env.NODE_ENV === 'development' ? '' : 'http://localhost:5001';
  const isTeacher = currentUser.role === 'teacher' || currentUser.role === 'admin';

  useEffect(() => {
    fetchClassDetails();
    if (isTeacher) {
      fetchStudents();
    }
  }, [classes]);

  const fetchClassDetails = async () => {
    try {
      setLoading(true);
      const detailedClasses = await Promise.all(
        classes.map(async (cls) => {
          try {
            const response = await fetch(`${API_BASE}/api/classes/${cls.id}/students`, {
              credentials: 'include',
            });
            
            if (response.ok) {
              const studentsData = await response.json();
              return {
                ...cls,
                student_count: studentsData.students?.length || 0,
                students: studentsData.students || []
              };
            }
            
            return {
              ...cls,
              student_count: 0,
              students: []
            };
          } catch (err) {
            console.error(`Error fetching students for class ${cls.id}:`, err);
            return {
              ...cls,
              student_count: 0,
              students: []
            };
          }
        })
      );
      
      setClassDetails(detailedClasses);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch class details');
    } finally {
      setLoading(false);
    }
  };

  const fetchStudents = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/students`, {
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Failed to fetch students');
      }

      const data = await response.json();
      setStudents(data.students || []);
    } catch (err) {
      console.error('Error fetching students:', err);
    }
  };

  const createClass = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/classes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Failed to create class');
      }

      onClassesUpdate();
      resetForm();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create class');
    }
  };

  const enrollStudent = async (classId: number, studentId: number) => {
    try {
      const response = await fetch(`${API_BASE}/api/classes/${classId}/enroll`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ student_id: studentId }),
      });

      if (!response.ok) {
        throw new Error('Failed to enroll student');
      }

      fetchClassDetails();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to enroll student');
    }
  };

  const unenrollStudent = async (classId: number, studentId: number) => {
    try {
      const response = await fetch(`${API_BASE}/api/classes/${classId}/unenroll`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ student_id: studentId }),
      });

      if (!response.ok) {
        throw new Error('Failed to unenroll student');
      }

      fetchClassDetails();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to unenroll student');
    }
  };

  const toggleClassStatus = async (classId: number, currentStatus: boolean) => {
    try {
      const response = await fetch(`${API_BASE}/api/classes/${classId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ is_active: !currentStatus }),
      });

      if (!response.ok) {
        throw new Error('Failed to update class status');
      }

      onClassesUpdate();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update class status');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      is_active: true
    });
    setShowCreateForm(false);
  };

  const openEnrollmentManager = (classItem: ClassDetails) => {
    setSelectedClass(classItem);
    setShowEnrollmentManager(true);
  };

  const closeEnrollmentManager = () => {
    setSelectedClass(null);
    setShowEnrollmentManager(false);
  };

  const getAvailableStudents = () => {
    if (!selectedClass) return [];
    const enrolledIds = selectedClass.students?.map(s => s.id) || [];
    return students.filter(student => !enrolledIds.includes(student.id));
  };

  if (loading) {
    return <div className="loading">Loading classroom data...</div>;
  }

  return (
    <div className="tab-content">
      <div className="classroom-manager-container">
        <div className="classroom-manager-header">
          <h2>Classroom Manager</h2>
          
          {isTeacher && (
            <div className="classroom-controls">
              <button
                onClick={() => setShowCreateForm(true)}
                className="create-class-button"
              >
                ➕ Create Class
              </button>
            </div>
          )}
        </div>

        {error && <div className="error-message">{error}</div>}

        {showCreateForm && isTeacher && (
          <div className="create-class-form">
            <h3>Create New Class</h3>
            
            <input
              type="text"
              placeholder="Class name..."
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              className="class-name-input"
            />

            <textarea
              placeholder="Class description..."
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              className="class-description-textarea"
              rows={3}
            />

            <label className="active-checkbox">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData(prev => ({ ...prev, is_active: e.target.checked }))}
              />
              ✅ Active Class
            </label>

            <div className="form-actions">
              <button
                onClick={createClass}
                className="submit-button"
                disabled={!formData.name.trim()}
              >
                Create Class
              </button>
              <button onClick={resetForm} className="cancel-button">
                Cancel
              </button>
            </div>
          </div>
        )}

        <div className="classes-grid">
          {classDetails.length === 0 ? (
            <div className="no-data">No classes available</div>
          ) : (
            classDetails.map(classItem => (
              <div key={classItem.id} className={`class-card ${!classItem.is_active ? 'inactive' : ''}`}>
                <div className="class-header">
                  <h3 className="class-title">{classItem.name}</h3>
                  <div className="class-badges">
                    <span 
                      className={`status-badge ${classItem.is_active ? 'active' : 'inactive'}`}
                    >
                      {classItem.is_active ? 'Active' : 'Inactive'}
                    </span>
                    <span className="enrollment-badge">
                      👥 {classItem.student_count} students
                    </span>
                  </div>
                </div>

                {classItem.description && (
                  <p className="class-description">{classItem.description}</p>
                )}

                <div className="class-meta">
                  <div className="class-teacher">
                    👨‍🏫 Teacher: <strong>{classItem.teacher_name || 'Unknown'}</strong>
                  </div>
                  
                  {classItem.students && classItem.students.length > 0 && (
                    <div className="class-students-preview">
                      <strong>Recent Students:</strong>
                      <div className="students-list">
                        {classItem.students.slice(0, 3).map(student => (
                          <span key={student.id} className="student-chip">
                            {student.name}
                          </span>
                        ))}
                        {classItem.students.length > 3 && (
                          <span className="more-students">
                            +{classItem.students.length - 3} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                <div className="class-actions">
                  {isTeacher && (
                    <div className="teacher-actions">
                      <button
                        onClick={() => openEnrollmentManager(classItem)}
                        className="manage-enrollment-button"
                        title="Manage student enrollment"
                      >
                        👥 Manage Enrollment
                      </button>
                      
                      <button
                        onClick={() => toggleClassStatus(classItem.id, classItem.is_active)}
                        className={`status-toggle-button ${classItem.is_active ? 'deactivate' : 'activate'}`}
                        title={classItem.is_active ? 'Deactivate class' : 'Activate class'}
                      >
                        {classItem.is_active ? '⏸️ Deactivate' : '▶️ Activate'}
                      </button>
                    </div>
                  )}

                  {!isTeacher && (
                    <div className="student-actions">
                      <div className="enrollment-status">
                        ✅ You are enrolled in this class
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Enrollment Manager Modal */}
        {showEnrollmentManager && selectedClass && (
          <div className="modal-overlay">
            <div className="enrollment-manager-modal">
              <div className="modal-header">
                <h3>Manage Enrollment - {selectedClass.name}</h3>
                <button onClick={closeEnrollmentManager} className="close-modal-button">
                  ✖️
                </button>
              </div>

              <div className="modal-content">
                <div className="enrolled-students-section">
                  <h4>Enrolled Students ({selectedClass.students?.length || 0})</h4>
                  
                  {selectedClass.students && selectedClass.students.length > 0 ? (
                    <div className="enrolled-students-list">
                      {selectedClass.students.map(student => (
                        <div key={student.id} className="enrolled-student-item">
                          <div className="student-info">
                            <strong>{student.name}</strong>
                            <span className="student-id">({student.student_id})</span>
                          </div>
                          <button
                            onClick={() => unenrollStudent(selectedClass.id, student.id)}
                            className="unenroll-button"
                            title="Remove from class"
                          >
                            ➖ Unenroll
                          </button>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="no-students">No students enrolled yet</div>
                  )}
                </div>

                <div className="available-students-section">
                  <h4>Available Students ({getAvailableStudents().length})</h4>
                  
                  {getAvailableStudents().length > 0 ? (
                    <div className="available-students-list">
                      {getAvailableStudents().map(student => (
                        <div key={student.id} className="available-student-item">
                          <div className="student-info">
                            <strong>{student.name}</strong>
                            <span className="student-id">({student.student_id})</span>
                          </div>
                          <button
                            onClick={() => enrollStudent(selectedClass.id, student.id)}
                            className="enroll-button"
                            title="Add to class"
                          >
                            ➕ Enroll
                          </button>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="no-students">All students are already enrolled</div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ClassroomManager; 