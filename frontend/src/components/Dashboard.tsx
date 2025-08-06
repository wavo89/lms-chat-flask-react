import React, { useState, useEffect } from 'react';
import './Dashboard.css';
import { useTheme } from '../contexts/ThemeContext';
import { DashboardProps, Class } from '../types';
import AttendanceManager from './AttendanceManager';
import GradesManager from './GradesManager';
import StudentsList from './StudentsList';
import ChatHistoryViewer from './ChatHistoryViewer';
import MessageBoard from './MessageBoard';
import TaskManager from './TaskManager';
import QuizMaker from './QuizMaker';
import ClassroomManager from './ClassroomManager';

const Dashboard: React.FC<DashboardProps> = ({ currentUser, onLogout }) => {
  const { isDark, toggleTheme } = useTheme();
  const [activeTab, setActiveTab] = useState(() => {
    // Restore last active tab from localStorage
    return localStorage.getItem('lms-active-tab') || 'attendance';
  });
  const [classes, setClasses] = useState<Class[]>([]);

  const API_BASE = process.env.NODE_ENV === 'development' ? '' : 'http://localhost:5001';
  const isTeacher = currentUser.role === 'teacher' || currentUser.role === 'admin';

  useEffect(() => {
    // Fetch classes when component mounts
    fetchClasses();
  }, []);

  // Save active tab to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('lms-active-tab', activeTab);
  }, [activeTab]);

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

  const renderTabContent = () => {
    switch (activeTab) {
      case 'attendance':
        if (isTeacher) {
          return <AttendanceManager currentUser={currentUser} classes={classes} />;
        } else {
          return <StudentsList currentUser={currentUser} />;
        }

      case 'grades':
        return <GradesManager currentUser={currentUser} classes={classes} />;

      case 'chat-history':
        if (isTeacher) {
          return <ChatHistoryViewer currentUser={currentUser} />;
        } else {
          return null;
        }

      case 'message-board':
        return <MessageBoard currentUser={currentUser} />;

      case 'tasks':
        return <TaskManager currentUser={currentUser} />;

      case 'quizzes':
        if (isTeacher) {
          return <QuizMaker currentUser={currentUser} classes={classes} />;
        } else {
          return <QuizMaker currentUser={currentUser} classes={classes} />;
        }

      case 'classroom':
        if (isTeacher) {
          return <ClassroomManager currentUser={currentUser} classes={classes} onClassesUpdate={fetchClasses} />;
        } else {
          return null;
        }

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

      <div className="dashboard-main">
        <div className="dashboard-navigation">
          <div className="nav-tabs">
            <button 
              className={`nav-tab ${activeTab === 'attendance' ? 'active' : ''}`}
              onClick={() => setActiveTab('attendance')}
            >
              {isTeacher ? 'Attendance' : 'Students'}
            </button>
            <button 
              className={`nav-tab ${activeTab === 'grades' ? 'active' : ''}`}
              onClick={() => setActiveTab('grades')}
            >
              Grades
            </button>
            {isTeacher && (
              <button 
                className={`nav-tab ${activeTab === 'chat-history' ? 'active' : ''}`}
                onClick={() => setActiveTab('chat-history')}
              >
                Chat History
              </button>
            )}
            <button 
              className={`nav-tab ${activeTab === 'message-board' ? 'active' : ''}`}
              onClick={() => setActiveTab('message-board')}
            >
              Message Board
            </button>
            <button 
              className={`nav-tab ${activeTab === 'tasks' ? 'active' : ''}`}
              onClick={() => setActiveTab('tasks')}
            >
              Tasks
            </button>
            <button 
              className={`nav-tab ${activeTab === 'quizzes' ? 'active' : ''}`}
              onClick={() => setActiveTab('quizzes')}
            >
              Quizzes
            </button>
            {isTeacher && (
              <button 
                className={`nav-tab ${activeTab === 'classroom' ? 'active' : ''}`}
                onClick={() => setActiveTab('classroom')}
              >
                Classroom
              </button>
            )}
          </div>
        </div>

        {renderTabContent()}
      </div>
    </div>
  );
};

export default Dashboard; 