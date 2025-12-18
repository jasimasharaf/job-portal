from rest_framework import generics, filters
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Prefetch
from .models import Job, JobApplication
from .serializers import JobSerializer
from .filters import JobFilter


class OptimizedJobListView(generics.ListAPIView):
    """
    Optimized Job List API with Search, Filter, and Ordering
    
    Features:
    - Search across multiple fields
    - Advanced filtering options
    - Sorting/ordering capabilities
    - Optimized queryset with prefetch_related
    - Pagination support
    """
    
    serializer_class = JobSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = JobFilter
    
    # Search configuration
    search_fields = [
        'title',
        'description', 
        'skills_required',
        'company_name',
        'location',
        'posted_by__first_name',
        'posted_by__last_name'
    ]
    
    # Ordering configuration
    ordering_fields = [
        'created_at',
        'title', 
        'job_type',
        'salary_min',
        'salary_max',
        'applications_count'  # Custom field for application count
    ]
    
    ordering = ['-created_at']  # Default ordering
    
    def get_queryset(self):
        """
        Optimized queryset with:
        - Select related for foreign keys
        - Prefetch related for reverse foreign keys
        - Annotation for application count
        - Only active jobs
        """
        return Job.objects.filter(is_active=True).select_related(
            'posted_by'
        ).prefetch_related(
            Prefetch(
                'applications',
                queryset=JobApplication.objects.select_related('applicant')
            )
        ).annotate(
            applications_count=Count('applications')
        )
    
    def list(self, request, *args, **kwargs):
        """Custom list method with enhanced response"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Get total count before pagination
        total_count = queryset.count()
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            
            # Add custom metadata
            paginated_response.data.update({
                'message': 'Jobs retrieved successfully',
                'total_count': total_count,
                'filters_applied': self.get_applied_filters(),
                'available_filters': self.get_available_filters()
            })
            
            return paginated_response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'message': 'Jobs retrieved successfully',
            'count': total_count,
            'data': serializer.data,
            'filters_applied': self.get_applied_filters(),
            'available_filters': self.get_available_filters()
        })
    
    def get_applied_filters(self):
        """Get currently applied filters"""
        applied_filters = {}
        
        for param, value in self.request.query_params.items():
            if param in ['search', 'title', 'company', 'location', 'job_type', 
                        'experience_level', 'posted_after', 'posted_before',
                        'salary_min', 'salary_max', 'skills', 
                        'publisher_first_name', 'publisher_last_name', 'ordering']:
                applied_filters[param] = value
        
        return applied_filters
    
    def get_available_filters(self):
        """Get available filter options"""
        return {
            'job_types': [{'value': choice[0], 'label': choice[1]} for choice in Job.JOB_TYPE_CHOICES],
            'experience_levels': [{'value': choice[0], 'label': choice[1]} for choice in Job.EXPERIENCE_CHOICES],
            'locations': list(Job.objects.filter(is_active=True).values_list('location', flat=True).distinct()),
            'companies': list(Job.objects.filter(is_active=True).values_list('company_name', flat=True).distinct()),
            'ordering_options': [
                {'value': 'created_at', 'label': 'Oldest First'},
                {'value': '-created_at', 'label': 'Newest First'},
                {'value': 'title', 'label': 'Title A-Z'},
                {'value': '-title', 'label': 'Title Z-A'},
                {'value': 'applications_count', 'label': 'Least Applied'},
                {'value': '-applications_count', 'label': 'Most Applied'},
                {'value': 'salary_min', 'label': 'Lowest Salary'},
                {'value': '-salary_max', 'label': 'Highest Salary'}
            ]
        }


class JobSearchStatsView(generics.GenericAPIView):
    """
    Get search statistics and aggregated data
    """
    
    def get(self, request):
        """Get job statistics"""
        try:
            stats = {
                'total_jobs': Job.objects.filter(is_active=True).count(),
                'jobs_by_type': dict(
                    Job.objects.filter(is_active=True)
                    .values_list('job_type')
                    .annotate(count=Count('id'))
                ),
                'jobs_by_experience': dict(
                    Job.objects.filter(is_active=True)
                    .values_list('experience_level')
                    .annotate(count=Count('id'))
                ),
                'top_companies': list(
                    Job.objects.filter(is_active=True)
                    .values('company_name')
                    .annotate(job_count=Count('id'))
                    .order_by('-job_count')[:10]
                ),
                'top_locations': list(
                    Job.objects.filter(is_active=True)
                    .values('location')
                    .annotate(job_count=Count('id'))
                    .order_by('-job_count')[:10]
                ),
                'recent_jobs_count': Job.objects.filter(
                    is_active=True
                ).count()  # Simplified for now
            }
            
            return Response({
                'message': 'Job statistics retrieved successfully',
                'data': stats
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)