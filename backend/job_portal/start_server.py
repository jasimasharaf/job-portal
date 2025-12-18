#!/usr/bin/env python
"""
Simple script to start the Django development server and test the authentication system
"""
import os
import sys
import subprocess
import time
import threading

def run_server():
    """Start Django development server"""
    print("Starting Django development server...")
    try:
        subprocess.run([sys.executable, "manage.py", "runserver", "127.0.0.1:8000"], 
                      cwd=os.path.dirname(os.path.abspath(__file__)))
    except KeyboardInterrupt:
        print("\nServer stopped.")

def show_endpoints():
    """Display available API endpoints"""
    print("\n" + "="*60)
    print("JOB PORTAL AUTHENTICATION API ENDPOINTS")
    print("="*60)
    print("Base URL: http://127.0.0.1:8000/auth/")
    print()
    print("Registration & Email Verification:")
    print("  POST /auth/register/           - Register new user")
    print("  POST /auth/verify-email/       - Verify email with OTP")
    print("  POST /auth/resend-otp/         - Resend OTP")
    print()
    print("Authentication:")
    print("  POST /auth/login/              - User login")
    print("  POST /auth/token/refresh/      - Refresh JWT token")
    print()
    print("Password Management:")
    print("  POST /auth/forgot-password/    - Request password reset")
    print("  POST /auth/verify-forgot-password/ - Verify reset OTP")
    print("  POST /auth/reset-password/     - Reset password")
    print("  POST /auth/change-password/    - Change password (authenticated)")
    print()
    print("User Profile:")
    print("  GET  /auth/profile/            - Get user profile (authenticated)")
    print()
    print("Admin Panel: http://127.0.0.1:8000/admin/")
    print("="*60)
    print()
    print("Sample Registration Request:")
    print('''
{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!",
    "job_role": "Software Developer"
}
    ''')
    print("="*60)

if __name__ == "__main__":
    show_endpoints()
    
    print("Press Ctrl+C to stop the server")
    print("Starting server in 3 seconds...")
    time.sleep(3)
    
    try:
        run_server()
    except KeyboardInterrupt:
        print("\nShutting down...")