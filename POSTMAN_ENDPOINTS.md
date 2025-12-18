# 🚀 Job Portal - Postman Endpoints Collection

## Base URL
```
http://127.0.0.1:8000/jobs/
```

## 📋 **1. Basic Job List**
```
GET http://127.0.0.1:8000/jobs/
```

## 🔍 **2. Search Endpoints**

### Text Search
```
GET http://127.0.0.1:8000/jobs/?search=python
GET http://127.0.0.1:8000/jobs/?search=developer
GET http://127.0.0.1:8000/jobs/?search=google
```

### Search in Specific Fields
```
GET http://127.0.0.1:8000/jobs/?title=developer
GET http://127.0.0.1:8000/jobs/?company=google
GET http://127.0.0.1:8000/jobs/?location=remote
```

### Publisher Search
```
GET http://127.0.0.1:8000/jobs/?publisher_first_name=john
GET http://127.0.0.1:8000/jobs/?publisher_last_name=smith
```

## 🎛️ **3. Filter Endpoints**

### Job Type Filters
```
GET http://127.0.0.1:8000/jobs/?job_type=full_time
GET http://127.0.0.1:8000/jobs/?job_type=full_time&job_type=part_time
GET http://127.0.0.1:8000/jobs/?job_type=contract,internship
```

### Experience Level
```
GET http://127.0.0.1:8000/jobs/?experience_level=junior
GET http://127.0.0.1:8000/jobs/?experience_level=mid&experience_level=senior
```

### Date Range Filters
```
GET http://127.0.0.1:8000/jobs/?posted_after=2025-01-01
GET http://127.0.0.1:8000/jobs/?posted_before=2025-12-31
GET http://127.0.0.1:8000/jobs/?posted_after=2025-01-01&posted_before=2025-12-31
```

### Salary Filters
```
GET http://127.0.0.1:8000/jobs/?salary_min=50000
GET http://127.0.0.1:8000/jobs/?salary_max=100000
GET http://127.0.0.1:8000/jobs/?salary_min=50000&salary_max=100000
```

### Skills Filter
```
GET http://127.0.0.1:8000/jobs/?skills=python,django
GET http://127.0.0.1:8000/jobs/?skills=javascript,react,node
```

## 📊 **4. Ordering/Sorting Endpoints**

### Date Sorting
```
GET http://127.0.0.1:8000/jobs/?ordering=created_at          # Oldest first
GET http://127.0.0.1:8000/jobs/?ordering=-created_at         # Newest first
```

### Title Sorting
```
GET http://127.0.0.1:8000/jobs/?ordering=title               # A-Z
GET http://127.0.0.1:8000/jobs/?ordering=-title              # Z-A
```

### Application Count Sorting
```
GET http://127.0.0.1:8000/jobs/?ordering=applications_count   # Least applied
GET http://127.0.0.1:8000/jobs/?ordering=-applications_count  # Most applied
```

### Salary Sorting
```
GET http://127.0.0.1:8000/jobs/?ordering=salary_min          # Lowest salary
GET http://127.0.0.1:8000/jobs/?ordering=-salary_max         # Highest salary
```

## 🔄 **5. Pagination Endpoints**

```
GET http://127.0.0.1:8000/jobs/?page=1
GET http://127.0.0.1:8000/jobs/?page=2&page_size=5
GET http://127.0.0.1:8000/jobs/?page=3&page_size=20
```

## 🎯 **6. Combined Search + Filter + Sort**

### Complex Query 1
```
GET http://127.0.0.1:8000/jobs/?search=python&job_type=full_time&location=remote&ordering=-created_at
```

### Complex Query 2
```
GET http://127.0.0.1:8000/jobs/?title=developer&experience_level=senior&salary_min=80000&ordering=-applications_count
```

### Complex Query 3
```
GET http://127.0.0.1:8000/jobs/?search=javascript&job_type=full_time&job_type=contract&posted_after=2025-01-01&ordering=title&page=2
```

### Complex Query 4
```
GET http://127.0.0.1:8000/jobs/?company=tech&skills=python,django&experience_level=mid&experience_level=senior&ordering=-salary_max
```

## 📈 **7. Statistics Endpoint**
```
GET http://127.0.0.1:8000/jobs/stats/
```

## 🔧 **8. Filter Options Endpoint**
```
GET http://127.0.0.1:8000/jobs/filters/
```

---

## 📝 **Postman Collection Setup**

### 1. Create New Collection
- **Name**: "Job Portal - Optimized Search & Filters"
- **Base URL Variable**: `{{base_url}}` = `http://127.0.0.1:8000`

### 2. Environment Variables
```json
{
  "base_url": "http://127.0.0.1:8000",
  "jobs_endpoint": "{{base_url}}/jobs/"
}
```

### 3. Test Requests

#### **Folder 1: Basic Search**
- **Request 1**: Basic List
  - `GET {{jobs_endpoint}}`
  
- **Request 2**: Text Search
  - `GET {{jobs_endpoint}}?search=python`

#### **Folder 2: Filtering**
- **Request 1**: Job Type Filter
  - `GET {{jobs_endpoint}}?job_type=full_time`
  
- **Request 2**: Multiple Filters
  - `GET {{jobs_endpoint}}?job_type=full_time&location=remote`

#### **Folder 3: Sorting**
- **Request 1**: Sort by Date
  - `GET {{jobs_endpoint}}?ordering=-created_at`
  
- **Request 2**: Sort by Popularity
  - `GET {{jobs_endpoint}}?ordering=-applications_count`

#### **Folder 4: Complex Queries**
- **Request 1**: Full Search
  - `GET {{jobs_endpoint}}?search=developer&job_type=full_time&experience_level=senior&ordering=-created_at&page=1`

#### **Folder 5: Utilities**
- **Request 1**: Get Stats
  - `GET {{jobs_endpoint}}stats/`
  
- **Request 2**: Get Filter Options
  - `GET {{jobs_endpoint}}filters/`

---

## 🧪 **Test Scenarios**

### **Scenario 1: Job Seeker Search**
```
GET {{jobs_endpoint}}?search=python&job_type=full_time&experience_level=junior&location=remote&ordering=-created_at
```

### **Scenario 2: Salary Range Search**
```
GET {{jobs_endpoint}}?salary_min=70000&salary_max=120000&experience_level=mid&experience_level=senior&ordering=-salary_max
```

### **Scenario 3: Skills-Based Search**
```
GET {{jobs_endpoint}}?skills=javascript,react,node&job_type=full_time&ordering=-applications_count
```

### **Scenario 4: Company Research**
```
GET {{jobs_endpoint}}?company=google&posted_after=2025-01-01&ordering=-created_at
```

### **Scenario 5: Popular Jobs**
```
GET {{jobs_endpoint}}?ordering=-applications_count&page_size=10
```

---

## 📊 **Expected Response Format**

```json
{
    "count": 150,
    "next": "http://127.0.0.1:8000/jobs/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Python Developer",
            "company_name": "Tech Corp",
            "location": "Remote",
            "job_type": "full_time",
            "experience_level": "mid",
            "salary_min": "70000.00",
            "salary_max": "90000.00",
            "applications_count": 15,
            "created_at": "2025-12-09T10:00:00Z",
            "posted_by_name": "John Smith",
            "posted_by_email": "john@techcorp.com"
        }
    ]
}
```

Copy these URLs directly into Postman to test the optimized search and filter functionality!