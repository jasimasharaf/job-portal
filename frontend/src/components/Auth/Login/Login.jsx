import React, { useState } from 'react';
import { authAPI } from '../../../api';
import './Login.css';

const Login = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const response = await authAPI.login({
        email: formData.email,
        password: formData.password
      });

      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      setMessage('✅ Login successful!');
      if (onSuccess) onSuccess();
    } catch (error) {
      setMessage('❌ Login failed: ' + (error.response?.data?.error || error.message));
    }
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="login-form">
      <div className="login-header">
        <h2 className="login-title">Welcome Back !</h2>
        <p className="login-subtitle">
          Log in to your account to connect with professionals and explore opportunities
        </p>
      </div>
      
      <div className="login-input-group">
        <input
          type="email"
          name="email"
          placeholder="Email"
          value={formData.email}
          onChange={handleInputChange}
          required
          className="login-input"
        />
      </div>
      
      <div className="login-input-group password">
        <input
          type="password"
          name="password"
          placeholder="Password"
          value={formData.password}
          onChange={handleInputChange}
          required
          className="login-input"
        />
      </div>
      
      <button 
        type="submit" 
        disabled={loading}
        className="login-button"
      >
        {loading ? 'Logging in...' : 'Login'}
      </button>
      
      <div className="social-divider">
        Or Continue With
      </div>
      
      <div className="social-buttons">
        <button type="button" className="social-button google">
          G
        </button>
        <button type="button" className="social-button facebook">
          f
        </button>
        <button type="button" className="social-button linkedin">
          in
        </button>
      </div>

      {message && (
        <div className={`login-message ${message.includes('✅') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}
    </form>
  );
};

export default Login;