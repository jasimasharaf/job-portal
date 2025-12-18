import React, { useState } from 'react';
import Login from './Login/Login';
import Signup from './Signup/Signup';
import './AuthPage.css';

const AuthPage = () => {
  const [currentView, setCurrentView] = useState('signup');

  return (
    <div className="auth-page">
      <div className="auth-container">
        
        {/* Left Side - Form */}
        <div className="auth-form-section">
          {/* Logo */}
          <div className="auth-logo">
            <h1>Logo</h1>
          </div>
          
          {/* Tabs */}
          <div className="auth-tabs">
            <button 
              onClick={() => setCurrentView('login')}
              className={`auth-tab ${currentView === 'login' ? 'active' : 'inactive'}`}
            >
              Login
            </button>
            <button 
              onClick={() => setCurrentView('signup')}
              className={`auth-tab ${currentView === 'signup' ? 'active' : 'inactive'}`}
            >
              Sign Up
            </button>
          </div>

          {/* Render Login or Signup Component */}
          {currentView === 'login' ? (
            <Login 
              onSuccess={() => console.log('Login successful')}
            />
          ) : (
            <Signup 
              onSwitchToLogin={() => setCurrentView('login')}
            />
          )}
        </div>

        {/* Right Side - Illustration */}
        <div className="auth-illustration">
          <img 
            src={currentView === 'signup' ? '/assets/images/signup-illustration.png' : '/assets/images/login-illustration.png'}
            alt={currentView === 'signup' ? 'Professional signup illustration' : 'Professional login illustration'}
          />
        </div>
      </div>
    </div>
  );
};

export default AuthPage;