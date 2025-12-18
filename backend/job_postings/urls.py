from django.urls import path
from .views import (
    JobCreateAPI, JobListAPI, JobDetailAPI, JobApplyAPI, MyJobsAPI, 
    JobUpdateAPI, MyApplicationsAPI, JobApplicationsReceivedAPI,
    ApplicationDetailAPI, UpdateApplicationStatusAPI, JobDeleteAPI,
    JobSearchAPI, JobFiltersAPI, JobTextSearchAPI, AvailableJobsAPI, JobFilterAPI
)
from .optimized_views import OptimizedJobListView, JobSearchStatsView

urlpatterns = [
    # Optimized Search & Filter (NEW)
    path('', OptimizedJobListView.as_view(), name='job-list-optimized'),
    path('stats/', JobSearchStatsView.as_view(), name='job-stats'),
    
    # Job Management
    path('create/', JobCreateAPI.as_view(), name='job-create'),
    path('list/', JobListAPI.as_view(), name='job-list'),
    path('available/', AvailableJobsAPI.as_view(), name='available-jobs'),
    path('search/', JobTextSearchAPI.as_view(), name='job-text-search'),
    path('advanced-search/', JobSearchAPI.as_view(), name='job-advanced-search'),
    path('filter/', JobFilterAPI.as_view(), name='job-filter'),
    path('filters/', JobFiltersAPI.as_view(), name='job-filters'),
    path('detail/<int:job_id>/', JobDetailAPI.as_view(), name='job-detail'),
    path('update/<int:job_id>/', JobUpdateAPI.as_view(), name='job-update'),
    path('delete/<int:job_id>/', JobDeleteAPI.as_view(), name='job-delete'),
    path('my-jobs/', MyJobsAPI.as_view(), name='my-jobs'),
    
    # Job Applications
    path('apply/<int:job_id>/', JobApplyAPI.as_view(), name='job-apply'),
    path('my-applications/', MyApplicationsAPI.as_view(), name='my-applications'),
    path('applications-received/', JobApplicationsReceivedAPI.as_view(), name='applications-received-all'),
    path('applications-received/<int:job_id>/', JobApplicationsReceivedAPI.as_view(), name='applications-received-job'),
    
    # Application Management
    path('application/<int:application_id>/', ApplicationDetailAPI.as_view(), name='application-detail'),
    path('application/<int:application_id>/update-status/', UpdateApplicationStatusAPI.as_view(), name='update-application-status'),
]