import React, { useState } from 'react';
import { authAPI } from '../../../api';
import './Signup.css';

const Signup = ({ onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    role: 'employee'
  });
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [agreedToTerms, setAgreedToTerms] = useState(false);

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
      await authAPI.register({
        email: formData.email,
        password: formData.password,
        first_name: formData.first_name,
        last_name: formData.last_name,
        role: formData.role
      });

      setMessage('✅ Registration successful! Please login.');
      if (onSwitchToLogin) onSwitchToLogin();
    } catch (error) {
      setMessage('❌ Registration failed: ' + (error.response?.data?.error || error.message));
    }
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="signup-form">
      <div className="signup-header">
        <h2 className="signup-title">Create an account</h2>
        <p className="signup-subtitle">
          Build your profile, connect with peers, and discover jobs
        </p>
      </div>
      
      <div className="signup-name-row">
        <input
          type="text"
          name="first_name"
          placeholder="First Name"
          value={formData.first_name}
          onChange={handleInputChange}
          required
          className="signup-input name"
        />
        <input
          type="text"
          name="last_name"
          placeholder="Last Name"
          value={formData.last_name}
          onChange={handleInputChange}
          required
          className="signup-input name"
        />
      </div>
      
      <div className="signup-input-group">
        <input
          type="email"
          name="email"
          placeholder="name@company.com"
          value={formData.email}
          onChange={handleInputChange}
          required
          className="signup-input"
        />
      </div>
      
      <div className="signup-input-group">
        <input
          type="password"
          name="password"
          placeholder="Password"
          value={formData.password}
          onChange={handleInputChange}
          required
          className="signup-input"
        />
      </div>
      
      <div className="signup-input-group">
        <select
          name="role"
          value={formData.role}
          onChange={handleInputChange}
          className="signup-select"
        >
          <option value="employee">Employee</option>
          <option value="employer">Employer</option>
          <option value="company">Company</option>
        </select>
      </div>
      
      <div className="signup-input-group terms">
        <label className="terms-label">
          <input 
            type="checkbox" 
            checked={agreedToTerms}
            onChange={(e) => setAgreedToTerms(e.target.checked)}
            className="terms-checkbox"
          />
          I agree to the Terms & Conditions and Privacy Policy
        </label>
      </div>
      
      <button 
        type="submit" 
        disabled={loading || !agreedToTerms}
        className={`signup-button ${(!agreedToTerms || loading) ? 'disabled' : 'enabled'}`}
      >
        {loading ? 'Creating Account...' : 'Create Account'}
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
        <div className={`signup-message ${message.includes('✅') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}
    </form>
  );
};

export default Signup;