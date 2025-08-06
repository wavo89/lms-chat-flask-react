import React, { useState, useEffect } from 'react';
import { Class, GradesResponse, User } from '../types';

interface GradesManagerProps {
  currentUser: User;
  classes: Class[];
}

const GradesManager: React.FC<GradesManagerProps> = ({ currentUser, classes }) => {
  const [selectedGradeClass, setSelectedGradeClass] = useState<number | null>(null);
  const [gradesData, setGradesData] = useState<GradesResponse | null>(null);
  const [loadingGrades, setLoadingGrades] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const API_BASE = process.env.NODE_ENV === 'development' ? '' : 'http://localhost:5001';

  useEffect(() => {
    // Fetch grades when grade class changes
    if (selectedGradeClass) {
      fetchGrades(selectedGradeClass);
    } else {
      setGradesData(null);
    }
  }, [selectedGradeClass]);

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
      // Update local state immediately for better UX
      if (gradesData) {
        const updatedGradesData = { ...gradesData };
        updatedGradesData.students = updatedGradesData.students.map(student => ({
          ...student,
          grades: {
            ...student.grades,
            ...Object.fromEntries(
              Object.entries(student.grades).map(([assignmentId, grade]) => [
                assignmentId,
                grade.id === gradeId 
                  ? { ...grade, points_earned: pointsEarned }
                  : grade
              ])
            )
          }
        }));
        setGradesData(updatedGradesData);
      }

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

      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update grade');
      // Revert local state on error
      if (selectedGradeClass !== null) {
        await fetchGrades(selectedGradeClass);
      }
    }
  };

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
                          <div className="assignment-name">{assignment.name}</div>
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
                              max="100"
                              step="1"
                              value={grade?.points_earned ?? ''}
                              onBlur={(e) => {
                                const value = e.target.value === '' ? null : parseInt(e.target.value);
                                // Ensure valid number
                                const numValue = value !== null && !isNaN(value) ? value : null;
                                // Validate range
                                if (numValue !== null && (numValue < 0 || numValue > 100)) {
                                  e.target.value = grade?.points_earned?.toString() ?? '';
                                  return;
                                }
                                if (grade?.id && numValue !== grade?.points_earned) {
                                  updateGrade(grade.id, numValue);
                                }
                              }}
                              onKeyDown={(e) => {
                                if (e.key === 'Enter') {
                                  e.currentTarget.blur();
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
};

export default GradesManager; 