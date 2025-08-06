import React, { useState, useEffect } from 'react';
import { User, Class } from '../types';

interface Quiz {
  id: number;
  title: string;
  description?: string;
  created_by: number;
  created_by_name?: string;
  class_id?: number;
  class_name?: string;
  is_published: boolean;
  time_limit?: number;
  max_attempts: number;
  due_date?: string;
  created_at: string;
  updated_at: string;
  question_count: number;
}

interface QuizMakerProps {
  currentUser: User;
  classes: Class[];
}

const QuizMaker: React.FC<QuizMakerProps> = ({ currentUser, classes }) => {
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingQuiz, setEditingQuiz] = useState<Quiz | null>(null);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    class_id: '',
    time_limit: '',
    max_attempts: '1',
    due_date: ''
  });

  const API_BASE = process.env.NODE_ENV === 'development' ? '' : 'http://localhost:5001';
  const isTeacher = currentUser.role === 'teacher' || currentUser.role === 'admin';

  useEffect(() => {
    fetchQuizzes();
  }, []);

  const fetchQuizzes = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/api/quizzes`, {
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Failed to fetch quizzes');
      }

      const data = await response.json();
      setQuizzes(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch quizzes');
    } finally {
      setLoading(false);
    }
  };

  const createQuiz = async () => {
    try {
      const payload = {
        ...formData,
        class_id: formData.class_id ? parseInt(formData.class_id) : null,
        time_limit: formData.time_limit ? parseInt(formData.time_limit) : null,
        max_attempts: parseInt(formData.max_attempts),
        due_date: formData.due_date || null
      };

      const response = await fetch(`${API_BASE}/api/quizzes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Failed to create quiz');
      }

      const newQuiz = await response.json();
      setQuizzes(prev => [newQuiz, ...prev]);
      resetForm();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create quiz');
    }
  };

  const updateQuiz = async () => {
    if (!editingQuiz) return;

    try {
      const payload = {
        ...formData,
        class_id: formData.class_id ? parseInt(formData.class_id) : null,
        time_limit: formData.time_limit ? parseInt(formData.time_limit) : null,
        max_attempts: parseInt(formData.max_attempts),
        due_date: formData.due_date || null
      };

      const response = await fetch(`${API_BASE}/api/quizzes/${editingQuiz.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Failed to update quiz');
      }

      const updatedQuiz = await response.json();
      setQuizzes(prev => prev.map(quiz => quiz.id === updatedQuiz.id ? updatedQuiz : quiz));
      resetForm();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update quiz');
    }
  };

  const togglePublishStatus = async (quizId: number, currentStatus: boolean) => {
    try {
      const response = await fetch(`${API_BASE}/api/quizzes/${quizId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ is_published: !currentStatus }),
      });

      if (!response.ok) {
        throw new Error('Failed to update quiz status');
      }

      const updatedQuiz = await response.json();
      setQuizzes(prev => prev.map(quiz => quiz.id === updatedQuiz.id ? updatedQuiz : quiz));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update quiz status');
    }
  };

  const startEdit = (quiz: Quiz) => {
    setEditingQuiz(quiz);
    setFormData({
      title: quiz.title,
      description: quiz.description || '',
      class_id: quiz.class_id?.toString() || '',
      time_limit: quiz.time_limit?.toString() || '',
      max_attempts: quiz.max_attempts.toString(),
      due_date: quiz.due_date ? quiz.due_date.split('T')[0] : ''
    });
    setShowCreateForm(true);
  };

  const resetForm = () => {
    setEditingQuiz(null);
    setFormData({
      title: '',
      description: '',
      class_id: '',
      time_limit: '',
      max_attempts: '1',
      due_date: ''
    });
    setShowCreateForm(false);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getDaysUntilDue = (dueDateString?: string) => {
    if (!dueDateString) return null;
    const dueDate = new Date(dueDateString);
    const today = new Date();
    const diffTime = dueDate.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  if (loading) {
    return <div className="loading">Loading quizzes...</div>;
  }

  return (
    <div className="tab-content">
      <div className="quiz-maker-container">
        <div className="quiz-maker-header">
          <h2>Quiz Maker</h2>
          
          {isTeacher && (
            <div className="quiz-controls">
              <button
                onClick={() => setShowCreateForm(true)}
                className="create-quiz-button"
              >
                ➕ Create Quiz
              </button>
            </div>
          )}
        </div>

        {error && <div className="error-message">{error}</div>}

        {showCreateForm && isTeacher && (
          <div className="create-quiz-form">
            <h3>{editingQuiz ? 'Edit Quiz' : 'Create New Quiz'}</h3>
            
            <input
              type="text"
              placeholder="Quiz title..."
              value={formData.title}
              onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
              className="quiz-title-input"
            />

            <textarea
              placeholder="Quiz description..."
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              className="quiz-description-textarea"
              rows={3}
            />

            <div className="quiz-form-row">
              <select
                value={formData.class_id}
                onChange={(e) => setFormData(prev => ({ ...prev, class_id: e.target.value }))}
                className="quiz-class-select"
              >
                <option value="">Select Class (Optional)</option>
                {classes.map(cls => (
                  <option key={cls.id} value={cls.id}>
                    {cls.name}
                  </option>
                ))}
              </select>

              <input
                type="number"
                placeholder="Time limit (minutes)"
                value={formData.time_limit}
                onChange={(e) => setFormData(prev => ({ ...prev, time_limit: e.target.value }))}
                className="quiz-time-input"
                min="1"
              />

              <input
                type="number"
                placeholder="Max attempts"
                value={formData.max_attempts}
                onChange={(e) => setFormData(prev => ({ ...prev, max_attempts: e.target.value }))}
                className="quiz-attempts-input"
                min="1"
              />

              <input
                type="datetime-local"
                value={formData.due_date}
                onChange={(e) => setFormData(prev => ({ ...prev, due_date: e.target.value }))}
                className="quiz-due-date-input"
              />
            </div>

            <div className="form-actions">
              <button
                onClick={editingQuiz ? updateQuiz : createQuiz}
                className="submit-button"
                disabled={!formData.title.trim()}
              >
                {editingQuiz ? 'Update Quiz' : 'Create Quiz'}
              </button>
              <button onClick={resetForm} className="cancel-button">
                Cancel
              </button>
            </div>
          </div>
        )}

        <div className="quizzes-grid">
          {quizzes.length === 0 ? (
            <div className="no-data">
              {isTeacher ? 'No quizzes created yet' : 'No quizzes available'}
            </div>
          ) : (
            quizzes.map(quiz => (
              <div key={quiz.id} className={`quiz-card ${!quiz.is_published ? 'draft' : ''}`}>
                <div className="quiz-header">
                  <h3 className="quiz-title">{quiz.title}</h3>
                  <div className="quiz-badges">
                    <span 
                      className={`status-badge ${quiz.is_published ? 'published' : 'draft'}`}
                    >
                      {quiz.is_published ? 'Published' : 'Draft'}
                    </span>
                    {quiz.question_count > 0 && (
                      <span className="questions-badge">
                        {quiz.question_count} Questions
                      </span>
                    )}
                  </div>
                </div>

                {quiz.description && (
                  <p className="quiz-description">{quiz.description}</p>
                )}

                <div className="quiz-meta">
                  {quiz.class_name && (
                    <div className="quiz-class">
                      📚 Class: <strong>{quiz.class_name}</strong>
                    </div>
                  )}
                  
                  <div className="quiz-details">
                    {quiz.time_limit && (
                      <span className="quiz-time">⏱️ {quiz.time_limit}min</span>
                    )}
                    <span className="quiz-attempts">🔄 {quiz.max_attempts} attempts</span>
                  </div>

                  {quiz.due_date && (
                    <div className={`quiz-due-date ${getDaysUntilDue(quiz.due_date)! < 0 ? 'overdue' : getDaysUntilDue(quiz.due_date)! <= 3 ? 'due-soon' : ''}`}>
                      📅 Due: {formatDate(quiz.due_date)}
                      {getDaysUntilDue(quiz.due_date) !== null && (
                        <span className="days-until">
                          {getDaysUntilDue(quiz.due_date)! < 0 
                            ? ` (${Math.abs(getDaysUntilDue(quiz.due_date)!)} days overdue)`
                            : getDaysUntilDue(quiz.due_date) === 0
                              ? ' (Due today)'
                              : ` (${getDaysUntilDue(quiz.due_date)} days left)`
                          }
                        </span>
                      )}
                    </div>
                  )}

                  <div className="quiz-created">
                    ✍️ Created by: <strong>{quiz.created_by_name}</strong> on {formatDate(quiz.created_at)}
                  </div>
                </div>

                <div className="quiz-actions">
                  {isTeacher && quiz.created_by === currentUser.id && (
                    <div className="teacher-actions">
                      <button
                        onClick={() => togglePublishStatus(quiz.id, quiz.is_published)}
                        className={`publish-button ${quiz.is_published ? 'unpublish' : 'publish'}`}
                        title={quiz.is_published ? 'Unpublish quiz' : 'Publish quiz'}
                      >
                        {quiz.is_published ? '📤 Unpublish' : '📢 Publish'}
                      </button>
                      
                      <button
                        onClick={() => startEdit(quiz)}
                        className="edit-quiz-button"
                        title="Edit quiz"
                      >
                        ✏️ Edit
                      </button>
                      
                      <button
                        className="manage-questions-button"
                        title="Manage questions"
                      >
                        ❓ Questions ({quiz.question_count})
                      </button>
                    </div>
                  )}

                  {!isTeacher && quiz.is_published && (
                    <div className="student-actions">
                      <button
                        className="take-quiz-button"
                        title="Take quiz"
                      >
                        📝 Take Quiz
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default QuizMaker; 