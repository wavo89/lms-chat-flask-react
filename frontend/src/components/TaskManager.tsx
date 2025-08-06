import React, { useState, useEffect } from 'react';
import { User } from '../types';
import '../styles/TaskManager.css';
import '../styles/SharedComponents.css';

interface Task {
  id: number;
  title: string;
  description?: string;
  assigned_to?: number;
  assigned_to_name?: string;
  created_by: number;
  created_by_name?: string;
  status: 'todo' | 'in_progress' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  due_date?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

interface TaskManagerProps {
  currentUser: User;
}

const TaskManager: React.FC<TaskManagerProps> = ({ currentUser }) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [students, setStudents] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterPriority, setFilterPriority] = useState<string>('all');

  const [formData, setFormData] = useState<{
    title: string;
    description: string;
    assigned_to: string;
    status: Task['status'];
    priority: Task['priority'];
    due_date: string;
  }>({
    title: '',
    description: '',
    assigned_to: '',
    status: 'todo',
    priority: 'medium',
    due_date: ''
  });

  const API_BASE = process.env.NODE_ENV === 'development' ? '' : 'http://localhost:5001';
  const isTeacher = currentUser.role === 'teacher' || currentUser.role === 'admin';

  useEffect(() => {
    fetchTasks();
    if (isTeacher) {
      fetchStudents();
    }
  }, []);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/api/tasks`, {
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Failed to fetch tasks');
      }

      const data = await response.json();
      setTasks(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tasks');
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

  const createTask = async () => {
    try {
      const payload = {
        ...formData,
        assigned_to: formData.assigned_to ? parseInt(formData.assigned_to) : null,
        due_date: formData.due_date || null
      };

      const response = await fetch(`${API_BASE}/api/tasks`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Failed to create task');
      }

      const newTask = await response.json();
      setTasks(prev => [newTask, ...prev]);
      resetForm();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create task');
    }
  };

  const updateTask = async () => {
    if (!editingTask) return;

    try {
      const payload = {
        ...formData,
        assigned_to: formData.assigned_to ? parseInt(formData.assigned_to) : null,
        due_date: formData.due_date || null
      };

      const response = await fetch(`${API_BASE}/api/tasks/${editingTask.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Failed to update task');
      }

      const updatedTask = await response.json();
      setTasks(prev => prev.map(task => task.id === updatedTask.id ? updatedTask : task));
      resetForm();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task');
    }
  };

  const deleteTask = async (taskId: number) => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/api/tasks/${taskId}`, {
        method: 'DELETE',
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Failed to delete task');
      }

      setTasks(prev => prev.filter(task => task.id !== taskId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete task');
    }
  };

  const startEdit = (task: Task) => {
    setEditingTask(task);
    setFormData({
      title: task.title,
      description: task.description || '',
      assigned_to: task.assigned_to?.toString() || '',
      status: task.status,
      priority: task.priority,
      due_date: task.due_date ? task.due_date.split('T')[0] : ''
    });
    setShowCreateForm(true);
  };

  const resetForm = () => {
    setEditingTask(null);
    setFormData({
      title: '',
      description: '',
      assigned_to: '',
      status: 'todo',
      priority: 'medium',
      due_date: ''
    });
    setShowCreateForm(false);
  };

  const quickUpdateStatus = async (taskId: number, status: string) => {
    try {
      const response = await fetch(`${API_BASE}/api/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ status }),
      });

      if (!response.ok) {
        throw new Error('Failed to update task status');
      }

      const updatedTask = await response.json();
      setTasks(prev => prev.map(task => task.id === updatedTask.id ? updatedTask : task));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task status');
    }
  };

  const filteredTasks = tasks.filter(task => {
    if (filterStatus !== 'all' && task.status !== filterStatus) return false;
    if (filterPriority !== 'all' && task.priority !== filterPriority) return false;
    return true;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'todo': return '#9E9E9E';
      case 'in_progress': return '#2196F3';
      case 'completed': return '#4CAF50';
      case 'cancelled': return '#f44336';
      default: return '#9E9E9E';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'low': return '#4CAF50';
      case 'medium': return '#FF9800';
      case 'high': return '#f44336';
      case 'urgent': return '#9C27B0';
      default: return '#9E9E9E';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const isOverdue = (dueDateString?: string) => {
    if (!dueDateString) return false;
    return new Date(dueDateString) < new Date() && !['completed', 'cancelled'].includes(filteredTasks.find(t => t.due_date === dueDateString)?.status || '');
  };

  if (loading) {
    return <div className="loading">Loading tasks...</div>;
  }

  return (
    <div className="tab-content">
      <div className="task-manager-container">
        <div className="task-manager-header">
          <h2>Task Management</h2>
          
          <div className="task-controls">
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="status-filter"
            >
              <option value="all">All Status</option>
              <option value="todo">To Do</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>

            <select
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value)}
              className="priority-filter"
            >
              <option value="all">All Priorities</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>

            <button
              onClick={() => setShowCreateForm(true)}
              className="create-task-button"
            >
              📝 New Task
            </button>
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}

        {showCreateForm && (
          <div className="create-task-form">
            <h3>{editingTask ? 'Edit Task' : 'Create New Task'}</h3>
            
            <input
              type="text"
              placeholder="Task title..."
              value={formData.title}
              onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
              className="task-title-input"
            />

            <textarea
              placeholder="Task description..."
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              className="task-description-textarea"
              rows={3}
            />

            <div className="task-form-row">
              {isTeacher && (
                <select
                  value={formData.assigned_to}
                  onChange={(e) => setFormData(prev => ({ ...prev, assigned_to: e.target.value }))}
                  className="task-assigned-select"
                >
                  <option value="">Assign to...</option>
                  {students.map(student => (
                    <option key={student.id} value={student.id}>
                      {student.name} ({student.student_id})
                    </option>
                  ))}
                </select>
              )}

              <select
                value={formData.status}
                onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value as Task['status'] }))}
                className="task-status-select"
              >
                <option value="todo">To Do</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>

              <select
                value={formData.priority}
                onChange={(e) => setFormData(prev => ({ ...prev, priority: e.target.value as Task['priority'] }))}
                className="task-priority-select"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>

              <input
                type="date"
                value={formData.due_date}
                onChange={(e) => setFormData(prev => ({ ...prev, due_date: e.target.value }))}
                className="task-due-date-input"
              />
            </div>

            <div className="form-actions">
              <button
                onClick={editingTask ? updateTask : createTask}
                className="submit-button"
                disabled={!formData.title.trim()}
              >
                {editingTask ? 'Update Task' : 'Create Task'}
              </button>
              <button onClick={resetForm} className="cancel-button">
                Cancel
              </button>
            </div>
          </div>
        )}

        <div className="tasks-grid">
          {filteredTasks.length === 0 ? (
            <div className="no-data">No tasks found</div>
          ) : (
            filteredTasks.map(task => (
              <div key={task.id} className={`task-card ${task.status} ${isOverdue(task.due_date) ? 'overdue' : ''}`}>
                <div className="task-header">
                  <h3 className="task-title">{task.title}</h3>
                  <div className="task-badges">
                    <span 
                      className="status-badge"
                      style={{ backgroundColor: getStatusColor(task.status) }}
                    >
                      {task.status.replace('_', ' ')}
                    </span>
                    <span 
                      className="priority-badge"
                      style={{ backgroundColor: getPriorityColor(task.priority) }}
                    >
                      {task.priority}
                    </span>
                  </div>
                </div>

                {task.description && (
                  <p className="task-description">{task.description}</p>
                )}

                <div className="task-meta">
                  {task.assigned_to_name && (
                    <div className="task-assigned">
                      👤 Assigned to: <strong>{task.assigned_to_name}</strong>
                    </div>
                  )}
                  <div className="task-creator">
                    ✍️ Created by: <strong>{task.created_by_name}</strong>
                  </div>
                  {task.due_date && (
                    <div className={`task-due-date ${isOverdue(task.due_date) ? 'overdue' : ''}`}>
                      📅 Due: {formatDate(task.due_date)}
                    </div>
                  )}
                </div>

                <div className="task-actions">
                  <div className="status-actions">
                    {task.status !== 'completed' && (
                      <button
                        onClick={() => quickUpdateStatus(task.id, 'completed')}
                        className="quick-action complete"
                        title="Mark as completed"
                      >
                        ✅
                      </button>
                    )}
                    {task.status === 'todo' && (
                      <button
                        onClick={() => quickUpdateStatus(task.id, 'in_progress')}
                        className="quick-action progress"
                        title="Start working"
                      >
                        🚀
                      </button>
                    )}
                  </div>

                  <div className="edit-actions">
                    {(task.created_by === currentUser.id || task.assigned_to === currentUser.id || isTeacher) && (
                      <>
                        <button
                          onClick={() => startEdit(task)}
                          className="edit-task-button"
                          title="Edit task"
                        >
                          ✏️
                        </button>
                        {(task.created_by === currentUser.id || isTeacher) && (
                          <button
                            onClick={() => deleteTask(task.id)}
                            className="delete-task-button"
                            title="Delete task"
                          >
                            🗑️
                          </button>
                        )}
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default TaskManager; 