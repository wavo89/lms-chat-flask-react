import React, { useState, useEffect } from 'react';
import { User } from '../types';

interface MessageBoardPost {
  id: number;
  user_id: number;
  user_name: string;
  user_role: string;
  title: string;
  content: string;
  category: string;
  is_pinned: boolean;
  created_at: string;
  updated_at: string;
}

interface MessageBoardProps {
  currentUser: User;
}

const MessageBoard: React.FC<MessageBoardProps> = ({ currentUser }) => {
  const [posts, setPosts] = useState<MessageBoardPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingPost, setEditingPost] = useState<MessageBoardPost | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    category: 'research',
    is_pinned: false
  });

  const API_BASE = process.env.NODE_ENV === 'development' ? '' : 'http://localhost:5001';
  const isTeacher = currentUser.role === 'teacher' || currentUser.role === 'admin';

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/api/message-board`, {
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Failed to fetch posts');
      }

      const data = await response.json();
      setPosts(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch posts');
    } finally {
      setLoading(false);
    }
  };

  const createPost = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/message-board`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Failed to create post');
      }

      const newPost = await response.json();
      setPosts(prev => [newPost, ...prev]);
      setFormData({ title: '', content: '', category: 'research', is_pinned: false });
      setShowCreateForm(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create post');
    }
  };

  const updatePost = async () => {
    if (!editingPost) return;

    try {
      const response = await fetch(`${API_BASE}/api/message-board/${editingPost.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Failed to update post');
      }

      const updatedPost = await response.json();
      setPosts(prev => prev.map(post => post.id === updatedPost.id ? updatedPost : post));
      setEditingPost(null);
      setFormData({ title: '', content: '', category: 'research', is_pinned: false });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update post');
    }
  };

  const deletePost = async (postId: number) => {
    if (!window.confirm('Are you sure you want to delete this post?')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/api/message-board/${postId}`, {
        method: 'DELETE',
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Failed to delete post');
      }

      setPosts(prev => prev.filter(post => post.id !== postId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete post');
    }
  };

  const startEdit = (post: MessageBoardPost) => {
    setEditingPost(post);
    setFormData({
      title: post.title,
      content: post.content,
      category: post.category,
      is_pinned: post.is_pinned
    });
    setShowCreateForm(true);
  };

  const cancelEdit = () => {
    setEditingPost(null);
    setFormData({ title: '', content: '', category: 'research', is_pinned: false });
    setShowCreateForm(false);
  };

  const filteredPosts = posts.filter(post => 
    categoryFilter === 'all' || post.category === categoryFilter
  );

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleDateString();
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'research': return '#4CAF50';
      case 'announcement': return '#2196F3';
      case 'question': return '#FF9800';
      default: return '#9E9E9E';
    }
  };

  if (loading) {
    return <div className="loading">Loading message board...</div>;
  }

  return (
    <div className="tab-content">
      <div className="message-board-container">
        <div className="message-board-header">
          <h2>Message Board</h2>
          
          <div className="message-board-controls">
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="category-filter"
            >
              <option value="all">All Categories</option>
              <option value="research">Research</option>
              <option value="announcement">Announcements</option>
              <option value="question">Questions</option>
            </select>

            <button
              onClick={() => setShowCreateForm(true)}
              className="create-post-button"
            >
              📝 New Post
            </button>
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}

        {showCreateForm && (
          <div className="create-post-form">
            <h3>{editingPost ? 'Edit Post' : 'Create New Post'}</h3>
            
            <input
              type="text"
              placeholder="Post title..."
              value={formData.title}
              onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
              className="post-title-input"
            />

            <select
              value={formData.category}
              onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
              className="post-category-select"
            >
              <option value="research">Research</option>
              <option value="announcement">Announcement</option>
              <option value="question">Question</option>
            </select>

            {isTeacher && (
              <label className="pin-checkbox">
                <input
                  type="checkbox"
                  checked={formData.is_pinned}
                  onChange={(e) => setFormData(prev => ({ ...prev, is_pinned: e.target.checked }))}
                />
                📌 Pin this post
              </label>
            )}

            <textarea
              placeholder="Write your message..."
              value={formData.content}
              onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
              className="post-content-textarea"
              rows={6}
            />

            <div className="form-actions">
              <button
                onClick={editingPost ? updatePost : createPost}
                className="submit-button"
                disabled={!formData.title.trim() || !formData.content.trim()}
              >
                {editingPost ? 'Update Post' : 'Create Post'}
              </button>
              <button onClick={cancelEdit} className="cancel-button">
                Cancel
              </button>
            </div>
          </div>
        )}

        <div className="posts-list">
          {filteredPosts.length === 0 ? (
            <div className="no-data">No posts found</div>
          ) : (
            filteredPosts.map(post => (
              <div key={post.id} className={`post-card ${post.is_pinned ? 'pinned' : ''}`}>
                <div className="post-header">
                  <div className="post-title-row">
                    {post.is_pinned && <span className="pin-icon">📌</span>}
                    <h3 className="post-title">{post.title}</h3>
                    <span 
                      className="post-category-badge"
                      style={{ backgroundColor: getCategoryColor(post.category) }}
                    >
                      {post.category}
                    </span>
                  </div>
                  
                  <div className="post-meta">
                    <span className="post-author">
                      by <strong>{post.user_name}</strong> ({post.user_role})
                    </span>
                    <span className="post-date">{formatDate(post.created_at)}</span>
                    
                    {(post.user_id === currentUser.id || isTeacher) && (
                      <div className="post-actions">
                        <button
                          onClick={() => startEdit(post)}
                          className="edit-post-button"
                          title="Edit post"
                        >
                          ✏️
                        </button>
                        <button
                          onClick={() => deletePost(post.id)}
                          className="delete-post-button"
                          title="Delete post"
                        >
                          🗑️
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                <div className="post-content">
                  {post.content.split('\n').map((line, index) => (
                    <p key={index}>{line}</p>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageBoard; 