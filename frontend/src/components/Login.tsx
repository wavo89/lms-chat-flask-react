import React, { useState } from 'react';
import './Login.css';

interface LoginProps {
  onLogin: (user: any) => void;
  onToggleMode: () => void;
  isRegisterMode: boolean;
}

const Login: React.FC<LoginProps> = ({ onLogin, onToggleMode, isRegisterMode }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const API_BASE = process.env.NODE_ENV === 'development' ? '' : 'http://localhost:5001';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const endpoint = isRegisterMode ? '/api/register' : '/api/login';
      const payload = isRegisterMode 
        ? { email: formData.email, password: formData.password, name: formData.name }
        : { email: formData.email, password: formData.password };

      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Authentication failed');
      }

      onLogin(data.user);
      setFormData({ email: '', password: '', name: '' });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h2>{isRegisterMode ? 'Create Account' : 'Welcome Back'}</h2>
          <p>{isRegisterMode ? 'Sign up to get started' : 'Sign in to your account'}</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {isRegisterMode && (
            <div className="form-group">
              <label htmlFor="name">Full Name</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required={isRegisterMode}
                placeholder="Enter your full name"
              />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="Enter your email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="Enter your password"
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="login-button" disabled={loading}>
            {loading ? 'Please wait...' : (isRegisterMode ? 'Create Account' : 'Sign In')}
          </button>
        </form>

        <div className="login-footer">
          <p>
            {isRegisterMode ? 'Already have an account?' : "Don't have an account?"}{' '}
            <button type="button" onClick={onToggleMode} className="toggle-mode-button">
              {isRegisterMode ? 'Sign In' : 'Sign Up'}
            </button>
          </p>
        </div>

        {!isRegisterMode && (
          <div className="demo-credentials">
            <h4>Demo Credentials:</h4>
            <p>📧 Email: test@test.com</p>
            <p>🔑 Password: Sample12</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Login; 