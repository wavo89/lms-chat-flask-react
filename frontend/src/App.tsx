import React, { useState, useEffect } from 'react';
import './App.css';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Chat from './components/Chat';
import { ThemeProvider } from './contexts/ThemeContext';

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

interface ApiResponse {
  users: User[];
  count: number;
}

function App() {
  const [loading, setLoading] = useState(true);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isRegisterMode, setIsRegisterMode] = useState(false);

  const API_BASE = process.env.NODE_ENV === 'development' ? '' : 'http://localhost:5001';

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/me`, {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        setCurrentUser(data);
        setIsAuthenticated(true);
      }
    } catch (err) {
      console.log('Not authenticated');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (user: User) => {
    setCurrentUser(user);
    setIsAuthenticated(true);
  };

  const handleLogout = async () => {
    try {
      await fetch(`${API_BASE}/api/logout`, {
        method: 'POST',
        credentials: 'include',
      });
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      setCurrentUser(null);
      setIsAuthenticated(false);
    }
  };

  const toggleRegisterMode = () => {
    setIsRegisterMode(!isRegisterMode);
  };

  if (loading) return (
    <ThemeProvider>
      <div className="loading">Loading...</div>
    </ThemeProvider>
  );
  
  if (!isAuthenticated) {
    return (
      <ThemeProvider>
        <Login 
          onLogin={handleLogin} 
          onToggleMode={toggleRegisterMode}
          isRegisterMode={isRegisterMode}
        />
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider>
      <div className="App">
        <div className="app-layout">
          <div className="dashboard-area">
            <Dashboard currentUser={currentUser!} onLogout={handleLogout} />
          </div>
          <div className="chat-area">
            <Chat currentUser={currentUser!} />
          </div>
        </div>
      </div>
    </ThemeProvider>
  );
}

export default App;
