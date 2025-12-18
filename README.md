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

## Installation

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/jasimasharaf/job-portal.git
cd job_portal/backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd ../frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

## API Documentation

The project includes Postman collections for API testing in the backend directory.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.