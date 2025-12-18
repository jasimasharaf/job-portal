# Job Portal Authentication - Troubleshooting Guide

## Quick Start

1. **Start the server:**
   ```bash
   python manage.py runserver
   ```
   Or use the helper script:
   ```bash
   python start_server.py
   ```

2. **Test the system:**
   ```bash
   python test_auth.py
   ```

## Common Issues & Solutions

### 1. "No module named 'rest_framework'"
**Solution:** Install required packages
```bash
pip install djangorestframework
pip install djangorestframework-simplejwt
```

### 2. "UserProfile matching query does not exist"
**Solution:** The views have been updated with proper error handling:
```python
profile, created = UserProfile.objects.get_or_create(user=user)
```

### 3. Email not sending
**Solution:** For development, emails are printed to console. Check your terminal output.

### 4. "Invalid credentials" on login
**Possible causes:**
- User not activated (email not verified)
- Wrong email/password
- User doesn't exist

### 5. OTP not working
**Check:**
- OTP expires in 5 minutes
- Case-sensitive OTP code
- User exists in database

## API Testing

### Register a new user:
```bash
curl -X POST http://127.0.0.1:8000/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!",
    "job_role": "Developer"
  }'
```

### Verify email:
```bash
curl -X POST http://127.0.0.1:8000/auth/verify-email/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "otp_code": "123456"
  }'
```

### Login:
```bash
curl -X POST http://127.0.0.1:8000/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

## Database Management

### Create superuser:
```bash
python manage.py createsuperuser
```

### Access admin panel:
Visit: http://127.0.0.1:8000/admin/

### Reset database:
```bash
del db.sqlite3
python manage.py migrate
```

## File Structure
```
job_portal/
├── authentication/
│   ├── models.py          # UserProfile, OTP models
│   ├── serializer.py      # API serializers
│   ├── views.py           # API endpoints
│   ├── urls.py            # URL routing
│   ├── utils.py           # Helper functions
│   └── admin.py           # Admin interface
├── job_portal/
│   ├── settings.py        # Django settings
│   └── urls.py            # Main URL config
├── test_auth.py           # System test script
├── test_api.py            # API test script
└── start_server.py        # Server startup script
```

## Environment Variables (Optional)
Create `.env` file:
```
SECRET_KEY=your-secret-key
DEBUG=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Next Steps
1. Set up proper email configuration for production
2. Add rate limiting for OTP requests
3. Implement user roles and permissions
4. Add API documentation with Swagger
5. Set up proper logging