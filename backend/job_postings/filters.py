import django_filters
from django.db.models import Q, Count
from .models import Job


class JobFilter(django_filters.FilterSet):
    # Search across multiple fields
    search = django_filters.CharFilter(method='filter_search', label='Search')
    
    # Title filter
    title = django_filters.CharFilter(lookup_expr='icontains', label='Job Title')
    
    # Company/Publisher filter
    company = django_filters.CharFilter(field_name='company_name', lookup_expr='icontains', label='Company')
    
    # Location filter
    location = django_filters.CharFilter(lookup_expr='icontains', label='Location')
    
    # Job type filter (supports multiple values)
    job_type = django_filters.MultipleChoiceFilter(
        choices=Job.JOB_TYPE_CHOICES,
        lookup_expr='in',
        label='Job Type'
    )
    
    # Experience level filter
    experience_level = django_filters.MultipleChoiceFilter(
        choices=Job.EXPERIENCE_CHOICES,
        lookup_expr='in',
        label='Experience Level'
    )
    
    # Date range filters
    posted_after = django_filters.DateFilter(field_name='created_at', lookup_expr='date__gte', label='Posted After')
    posted_before = django_filters.DateFilter(field_name='created_at', lookup_expr='date__lte', label='Posted Before')
    
    # Salary range filters
    salary_min = django_filters.NumberFilter(field_name='salary_min', lookup_expr='gte', label='Minimum Salary')
    salary_max = django_filters.NumberFilter(field_name='salary_max', lookup_expr='lte', label='Maximum Salary')
    
    # Skills filter
    skills = django_filters.CharFilter(method='filter_skills', label='Skills')
    
    # Publisher name filters
    publisher_first_name = django_filters.CharFilter(
        field_name='posted_by__first_name', 
        lookup_expr='icontains', 
        label='Publisher First Name'
    )
    publisher_last_name = django_filters.CharFilter(
        field_name='posted_by__last_name', 
        lookup_expr='icontains', 
        label='Publisher Last Name'
    )
    
    class Meta:
        model = Job
        fields = [
            'search', 'title', 'company', 'location', 'job_type', 
            'experience_level', 'posted_after', 'posted_before',
            'salary_min', 'salary_max', 'skills', 
            'publisher_first_name', 'publisher_last_name'
        ]
    
    def filter_search(self, queryset, name, value):
        """Search across multiple fields"""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(skills_required__icontains=value) |
            Q(company_name__icontains=value) |
            Q(location__icontains=value) |
            Q(posted_by__first_name__icontains=value) |
            Q(posted_by__last_name__icontains=value)
        )
    
    def filter_skills(self, queryset, name, value):
        """Filter by comma-separated skills"""
        if not value:
            return queryset
        
        skill_list = [skill.strip() for skill in value.split(',')]
        skill_query = Q()
        for skill in skill_list:
            skill_query |= Q(skills_required__icontains=skill)
        
        return queryset.filter(skill_query)