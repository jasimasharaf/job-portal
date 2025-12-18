# Job Portal - Search & Filters API Testing Guide

## Base URL
```
http://127.0.0.1:8000/api/jobs/
```

## 1. Basic Job List (Enhanced with Filters)
**Endpoint:** `GET /api/jobs/list/`

### Query Parameters:
- `search` - Search in title, description, company, skills, location
- `location` - Filter by location (partial match)
- `job_type` - Filter by job type (full_time, part_time, contract, internship)
- `experience_level` - Filter by experience (entry, junior, mid, senior)
- `company_name` - Filter by company name (partial match)
- `salary_min` - Minimum salary filter
- `salary_max` - Maximum salary filter
- `skills` - Comma-separated skills to search
- `date_from` - Jobs posted from date (YYYY-MM-DD)
- `date_to` - Jobs posted until date (YYYY-MM-DD)
- `sort_by` - Sort field (created_at, -created_at, title, -title, salary_min, -salary_min, etc.)
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 10, max: 50)

### Example Requests:

#### Basic Search
```
GET /api/jobs/list/?search=python
```

#### Multiple Filters
```
GET /api/jobs/list/?job_type=full_time&experience_level=mid&location=New York&salary_min=80000
```

#### Skills Search
```
GET /api/jobs/list/?skills=python,django,react
```

#### Date Range
```
GET /api/jobs/list/?date_from=2024-01-01&date_to=2024-12-31
```

#### Pagination & Sorting
```
GET /api/jobs/list/?page=2&page_size=5&sort_by=-salary_max
```

## 2. Advanced Job Search
**Endpoint:** `GET /api/jobs/search/`

### Enhanced Features:
- Multiple job types: `job_type=full_time&job_type=part_time`
- Multiple experience levels: `experience_level=mid&experience_level=senior`
- Better error handling for invalid dates/salaries
- Filter options included in response

### Example Requests:

#### Multiple Job Types
```
GET /api/jobs/search/?job_type=full_time&job_type=contract&location=Remote
```

#### Complex Search
```
GET /api/jobs/search/?search=developer&salary_min=70000&salary_max=120000&skills=javascript,node.js&sort_by=-created_at
```

#### Company & Location Filter
```
GET /api/jobs/search/?company_name=Tech Corp&location=San Francisco&experience_level=senior
```

## 3. Get Filter Options
**Endpoint:** `GET /api/jobs/filters/`

Returns available filter options for dropdowns:
- Job types with labels
- Experience levels with labels
- Available locations
- Available companies
- Salary ranges

### Example Response:
```json
{
    "message": "Filter options retrieved successfully",
    "data": {
        "job_types": [
            {"value": "full_time", "label": "Full Time"},
            {"value": "part_time", "label": "Part Time"},
            {"value": "contract", "label": "Contract"},
            {"value": "internship", "label": "Internship"}
        ],
        "experience_levels": [
            {"value": "entry", "label": "Entry Level (0-1 years)"},
            {"value": "junior", "label": "Junior (1-3 years)"},
            {"value": "mid", "label": "Mid Level (3-5 years)"},
            {"value": "senior", "label": "Senior (5+ years)"}
        ],
        "locations": ["New York", "San Francisco", "Remote", "London"],
        "companies": ["Tech Corp", "StartupXYZ", "BigTech Inc"],
        "salary_ranges": [
            {"min": 0, "max": 50000, "label": "Under $50K"},
            {"min": 50000, "max": 100000, "label": "$50K - $100K"},
            {"min": 100000, "max": 150000, "label": "$100K - $150K"},
            {"min": 150000, "max": null, "label": "Above $150K"}
        ]
    }
}
```

## Postman Collection Setup

### 1. Create New Collection
- Name: "Job Portal - Search & Filters"
- Add base URL as variable: `{{base_url}}` = `http://127.0.0.1:8000`

### 2. Add Requests

#### Request 1: Basic Job Search
- **Method:** GET
- **URL:** `{{base_url}}/api/jobs/list/`
- **Params:** 
  - search: python
  - job_type: full_time
  - page_size: 5

#### Request 2: Advanced Search with Multiple Filters
- **Method:** GET
- **URL:** `{{base_url}}/api/jobs/search/`
- **Params:**
  - search: developer
  - job_type: full_time
  - job_type: contract
  - experience_level: mid
  - salary_min: 70000
  - salary_max: 120000
  - location: Remote
  - sort_by: -salary_max

#### Request 3: Skills-based Search
- **Method:** GET
- **URL:** `{{base_url}}/api/jobs/search/`
- **Params:**
  - skills: python,django,react,javascript
  - experience_level: senior
  - sort_by: -created_at

#### Request 4: Date Range Filter
- **Method:** GET
- **URL:** `{{base_url}}/api/jobs/list/`
- **Params:**
  - date_from: 2024-01-01
  - date_to: 2024-12-31
  - sort_by: created_at

#### Request 5: Company & Location Filter
- **Method:** GET
- **URL:** `{{base_url}}/api/jobs/search/`
- **Params:**
  - company_name: Tech
  - location: New York
  - job_type: full_time

#### Request 6: Get Filter Options
- **Method:** GET
- **URL:** `{{base_url}}/api/jobs/filters/`

#### Request 7: Pagination Test
- **Method:** GET
- **URL:** `{{base_url}}/api/jobs/list/`
- **Params:**
  - page: 2
  - page_size: 3
  - sort_by: title

### 3. Test Scenarios

#### Scenario 1: Empty Search
Test with no parameters to get all jobs with pagination.

#### Scenario 2: No Results
Search for something that doesn't exist: `search=nonexistentjob`

#### Scenario 3: Invalid Parameters
Test with invalid dates, negative salaries, etc.

#### Scenario 4: Case Sensitivity
Test searches with different cases: `search=PYTHON` vs `search=python`

#### Scenario 5: Special Characters
Test with special characters in search terms.

## Response Format

All search endpoints return:
```json
{
    "message": "Jobs retrieved successfully",
    "count": 25,
    "page": 1,
    "page_size": 10,
    "total_pages": 3,
    "filter_options": {...},  // Only in /search/ endpoint
    "data": [...]
}
```

## Tips for Testing

1. **Start with Filter Options**: Call `/filters/` first to see available values
2. **Test Combinations**: Try different filter combinations
3. **Check Pagination**: Test with different page sizes
4. **Verify Sorting**: Test all sort options
5. **Edge Cases**: Test with empty results, invalid parameters
6. **Performance**: Test with large page sizes (up to 50)

## Common Filter Combinations

1. **Remote Jobs**: `location=Remote&job_type=full_time`
2. **Entry Level**: `experience_level=entry&salary_max=60000`
3. **High Paying**: `salary_min=100000&sort_by=-salary_max`
4. **Recent Posts**: `date_from=2024-12-01&sort_by=-created_at`
5. **Tech Skills**: `skills=python,javascript,react&experience_level=mid`