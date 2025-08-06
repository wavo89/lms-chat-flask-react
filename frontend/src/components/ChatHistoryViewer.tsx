import React, { useState, useEffect } from 'react';
import { User } from '../types';

interface ChatHistoryRecord {
  id: number;
  user_id: number;
  user_name: string;
  user_student_id: string;
  message: string;
  response: string;
  timestamp: string;
  session_id?: string;
}

interface ChatHistoryViewerProps {
  currentUser: User;
}

const ChatHistoryViewer: React.FC<ChatHistoryViewerProps> = ({ currentUser }) => {
  const [chatHistory, setChatHistory] = useState<ChatHistoryRecord[]>([]);
  const [selectedStudentId, setSelectedStudentId] = useState<number | null>(null);
  const [students, setStudents] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const API_BASE = process.env.NODE_ENV === 'development' ? '' : 'http://localhost:5001';

  useEffect(() => {
    fetchStudents();
    fetchChatHistory();
  }, [selectedStudentId]);

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
      setError(err instanceof Error ? err.message : 'Failed to fetch students');
    }
  };

  const fetchChatHistory = async () => {
    try {
      setLoading(true);
      const url = selectedStudentId 
        ? `${API_BASE}/api/chat-history?student_id=${selectedStudentId}`
        : `${API_BASE}/api/chat-history`;
      
      const response = await fetch(url, {
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Failed to fetch chat history');
      }

      const data = await response.json();
      setChatHistory(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch chat history');
    } finally {
      setLoading(false);
    }
  };

  const deleteChatRecord = async (chatId: number) => {
    if (!window.confirm('Are you sure you want to delete this chat record?')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/api/chat-history/${chatId}`, {
        method: 'DELETE',
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Failed to delete chat record');
      }

      // Remove from local state
      setChatHistory(prev => prev.filter(chat => chat.id !== chatId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete chat record');
    }
  };

  const filteredChatHistory = chatHistory.filter(chat =>
    chat.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
    chat.response.toLowerCase().includes(searchTerm.toLowerCase()) ||
    chat.user_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading) {
    return <div className="loading">Loading chat history...</div>;
  }

  return (
    <div className="tab-content">
      <div className="chat-history-container">
        <div className="chat-history-header">
          <h2>Student Chat History</h2>
          
          <div className="chat-history-controls">
            <select
              value={selectedStudentId || ''}
              onChange={(e) => setSelectedStudentId(e.target.value ? parseInt(e.target.value) : null)}
              className="student-selector"
            >
              <option value="">All Students</option>
              {students.map(student => (
                <option key={student.id} value={student.id}>
                  {student.name} ({student.student_id})
                </option>
              ))}
            </select>

            <input
              type="text"
              placeholder="Search conversations..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />

            <button onClick={fetchChatHistory} className="refresh-button">
              🔄 Refresh
            </button>
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}

        <div className="chat-history-list">
          {filteredChatHistory.length === 0 ? (
            <div className="no-data">No chat history found</div>
          ) : (
            filteredChatHistory.map(chat => (
              <div key={chat.id} className="chat-record">
                <div className="chat-record-header">
                  <div className="student-info">
                    <strong>{chat.user_name}</strong> ({chat.user_student_id})
                  </div>
                  <div className="chat-timestamp">
                    {formatDate(chat.timestamp)}
                  </div>
                  <button
                    onClick={() => deleteChatRecord(chat.id)}
                    className="delete-chat-button"
                    title="Delete this chat record"
                  >
                    🗑️
                  </button>
                </div>

                <div className="chat-conversation">
                  <div className="chat-message">
                    <div className="message-label">Student:</div>
                    <div className="message-content">{chat.message}</div>
                  </div>

                  <div className="chat-response">
                    <div className="message-label">AI Assistant:</div>
                    <div className="message-content">{chat.response}</div>
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

export default ChatHistoryViewer; 