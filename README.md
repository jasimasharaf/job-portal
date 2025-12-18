# Job Portal

A full-stack job portal application built with Django REST Framework (backend) and React (frontend).

## Features

- User authentication and authorization
- Job posting and application management
- User profiles (Employee, Employer, Company)
- Social feeds and posts
- User relationships and connections
- Advanced job search and filtering
- File uploads (resumes, profile images)

## Tech Stack

**Backend:**
- Django 4.x
- Django REST Framework
- SQLite (development)
- JWT Authentication

**Frontend:**
- React 18
- CSS3
- Axios for API calls

## Project Structure

```
job_portal/
├── backend/                     # Django backend
│   ├── authentication/         # User authentication app
│   ├── job_postings/           # Job posting and application management
│   ├── profile_app/            # User profiles and social features
│   ├── feeds/                  # Social feed functionality
│   ├── relationships/          # User connections
│   ├── core/                   # Core utilities and permissions
│   ├── job_portal/             # Django project settings
│   ├── manage.py
│   ├── requirements.txt
│   └── db.sqlite3              # (ignored)
│
├── frontend/                    # React frontend application
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── node_modules/           # (ignored)
│
├── .gitignore
└── README.md
```

## Quick Start

### Option 1: Run Both Servers (Recommended)
```bash
# Clone and navigate to project
git clone https://github.com/jasimasharaf/job-portal.git
cd job_portal

# Run both backend and frontend in separate terminals
start_project.bat
```

### Option 2: Manual Setup

#### Backend Setup (Terminal 1)
```bash
cd backend
# Create virtual environment
python -m venv venv
venv\Scripts\activate
# Install dependencies and run
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

#### Frontend Setup (Terminal 2)
```bash
cd frontend
# Install dependencies and run
npm install
npm start
```

## Servers
- **Backend**: http://127.0.0.1:8000 (Django + DRF)
- **Frontend**: http://localhost:3000 (React)
- **Database**: PostgreSQL

## API Documentation

The project includes Postman collections for API testing in the backend directory.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.