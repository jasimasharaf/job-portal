from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from .models import Job, JobApplication
from .serializers import (
    JobSerializer, JobCreateSerializer, JobApplicationCreateSerializer,
    JobApplicationListSerializer, JobApplicationDetailSerializer,
    ApplicationStatusUpdateSerializer, JobApplicationReceivedSerializer,
    JobSearchSerializer
)
from authentication.models import UserProfile


class JobCreateAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Check if user can post jobs
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'employee':
                return Response({
                    'error': 'Employees cannot post jobs'
                }, status=status.HTTP_403_FORBIDDEN)
            
            serializer = JobCreateSerializer(data=request.data, context={'request': request})
            
            if serializer.is_valid():
                job = serializer.save()
                return Response({
                    'message': 'Job posted successfully',
                    'data': JobSerializer(job).data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'User profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JobListAPI(APIView):
    def get(self, request):
        try:
            jobs = Job.objects.filter(is_active=True)
            
            # Search functionality
            search = request.query_params.get('search')
            if search:
                from django.db.models import Q
                jobs = jobs.filter(
                    Q(title__icontains=search) |
                    Q(description__icontains=search) |
                    Q(company_name__icontains=search) |
                    Q(skills_required__icontains=search) |
                    Q(location__icontains=search)
                )
            
            # Filter by location
            location = request.query_params.get('location')
            if location:
                jobs = jobs.filter(location__icontains=location)
            
            # Filter by job type
            job_type = request.query_params.get('job_type')
            if job_type:
                jobs = jobs.filter(job_type=job_type)
            
            # Filter by experience level
            experience_level = request.query_params.get('experience_level')
            if experience_level:
                jobs = jobs.filter(experience_level=experience_level)
            
            # Filter by company
            company_name = request.query_params.get('company_name')
            if company_name:
                jobs = jobs.filter(company_name__icontains=company_name)
            
            # Filter by salary range
            salary_min = request.query_params.get('salary_min')
            if salary_min:
                jobs = jobs.filter(salary_max__gte=salary_min)
            
            salary_max = request.query_params.get('salary_max')
            if salary_max:
                jobs = jobs.filter(salary_min__lte=salary_max)
            
            # Filter by skills
            skills = request.query_params.get('skills')
            if skills:
                skill_list = [skill.strip() for skill in skills.split(',')]
                from django.db.models import Q
                skill_query = Q()
                for skill in skill_list:
                    skill_query |= Q(skills_required__icontains=skill)
                jobs = jobs.filter(skill_query)
            
            # Date range filters
            date_from = request.query_params.get('date_from')
            if date_from:
                jobs = jobs.filter(created_at__date__gte=date_from)
            
            date_to = request.query_params.get('date_to')
            if date_to:
                jobs = jobs.filter(created_at__date__lte=date_to)
            
            # Sorting
            sort_by = request.query_params.get('sort_by', '-created_at')
            valid_sort_fields = ['created_at', '-created_at', 'title', '-title', 'salary_min', '-salary_min', 'salary_max', '-salary_max']
            if sort_by in valid_sort_fields:
                jobs = jobs.order_by(sort_by)
            
            # Pagination
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            start = (page - 1) * page_size
            end = start + page_size
            
            total_count = jobs.count()
            jobs_page = jobs[start:end]
            
            serializer = JobSerializer(jobs_page, many=True)
            return Response({
                'message': 'Jobs retrieved successfully',
                'count': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_count + page_size - 1) // page_size,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JobDetailAPI(APIView):
    def get(self, request, job_id):
        try:
            job = get_object_or_404(Job, id=job_id, is_active=True)
            serializer = JobSerializer(job)
            return Response({
                'message': 'Job retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Job not found'
            }, status=status.HTTP_404_NOT_FOUND)


class JobApplyAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, job_id):
        try:
            # Check if job exists first
            try:
                job = Job.objects.get(id=job_id, is_active=True)
            except Job.DoesNotExist:
                return Response({
                    'error': f'Job with ID {job_id} not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check if user can apply (employees and employers can apply)
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'company':
                return Response({
                    'error': 'Companies cannot apply for jobs'
                }, status=status.HTTP_403_FORBIDDEN)
            
            serializer = JobApplicationCreateSerializer(
                data=request.data,
                context={'request': request, 'job': job}
            )
            
            if serializer.is_valid():
                application = serializer.save()
                response_serializer = JobApplicationDetailSerializer(application, context={'request': request})
                return Response({
                    'message': 'Application submitted successfully',
                    'data': response_serializer.data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'User profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MyApplicationsAPI(APIView):
    """Employee/Employer: List jobs they applied for"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            applications = JobApplication.objects.filter(applicant=request.user)
            
            # Filter by status
            status_filter = request.query_params.get('status')
            if status_filter:
                applications = applications.filter(status=status_filter)
            
            # Search in job title or company
            search = request.query_params.get('search')
            if search:
                from django.db.models import Q
                applications = applications.filter(
                    Q(job__title__icontains=search) |
                    Q(job__company_name__icontains=search)
                )
            
            # Filter by date range
            date_from = request.query_params.get('date_from')
            if date_from:
                applications = applications.filter(applied_at__date__gte=date_from)
            
            date_to = request.query_params.get('date_to')
            if date_to:
                applications = applications.filter(applied_at__date__lte=date_to)
            
            # Sorting
            sort_by = request.query_params.get('sort_by', '-applied_at')
            valid_sort_fields = ['-applied_at', 'applied_at', 'status', '-status']
            if sort_by in valid_sort_fields:
                applications = applications.order_by(sort_by)
            
            # Pagination
            page = int(request.query_params.get('page', 1))
            page_size = min(int(request.query_params.get('page_size', 10)), 50)
            start = (page - 1) * page_size
            end = start + page_size
            
            total_count = applications.count()
            applications_page = applications[start:end]
            
            serializer = JobApplicationListSerializer(applications_page, many=True, context={'request': request})
            return Response({
                'message': 'Your applications retrieved successfully',
                'count': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_count + page_size - 1) // page_size,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JobApplicationsReceivedAPI(APIView):
    """Employer/Company: List applications received for their jobs"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, job_id=None):
        try:
            if job_id:
                # Applications for specific job
                job = get_object_or_404(Job, id=job_id, posted_by=request.user)
                applications = JobApplication.objects.filter(job=job)
            else:
                # All applications for user's jobs
                user_jobs = Job.objects.filter(posted_by=request.user)
                applications = JobApplication.objects.filter(job__in=user_jobs)
            
            # Filter by status
            status_filter = request.query_params.get('status')
            if status_filter:
                applications = applications.filter(status=status_filter)
            
            # Search in applicant name or job title
            search = request.query_params.get('search')
            if search:
                from django.db.models import Q
                applications = applications.filter(
                    Q(applicant__first_name__icontains=search) |
                    Q(applicant__last_name__icontains=search) |
                    Q(job__title__icontains=search)
                )
            
            # Filter by date range
            date_from = request.query_params.get('date_from')
            if date_from:
                applications = applications.filter(applied_at__date__gte=date_from)
            
            date_to = request.query_params.get('date_to')
            if date_to:
                applications = applications.filter(applied_at__date__lte=date_to)
            
            # Sorting
            sort_by = request.query_params.get('sort_by', '-applied_at')
            valid_sort_fields = ['-applied_at', 'applied_at', 'status', '-status']
            if sort_by in valid_sort_fields:
                applications = applications.order_by(sort_by)
            
            # Pagination
            page = int(request.query_params.get('page', 1))
            page_size = min(int(request.query_params.get('page_size', 10)), 50)
            start = (page - 1) * page_size
            end = start + page_size
            
            total_count = applications.count()
            applications_page = applications[start:end]
            
            serializer = JobApplicationReceivedSerializer(applications_page, many=True)
            return Response({
                'message': 'Applications retrieved successfully',
                'count': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_count + page_size - 1) // page_size,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ApplicationDetailAPI(APIView):
    """View detailed application"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, application_id):
        try:
            application = get_object_or_404(JobApplication, id=application_id)
            
            # Check permissions: applicant or job owner can view
            if application.applicant != request.user and application.job.posted_by != request.user:
                return Response({
                    'error': 'Access denied'
                }, status=status.HTTP_403_FORBIDDEN)
            
            serializer = JobApplicationDetailSerializer(application, context={'request': request})
            return Response({
                'message': 'Application details retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)


class UpdateApplicationStatusAPI(APIView):
    """Employer/Company: Update application status"""
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, application_id):
        try:
            application = get_object_or_404(JobApplication, id=application_id)
            
            serializer = ApplicationStatusUpdateSerializer(
                application, 
                data=request.data, 
                partial=True,
                context={'request': request}
            )
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': 'Application status updated successfully',
                    'data': JobApplicationDetailSerializer(application).data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)


class JobUpdateAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, job_id):
        try:
            # Get user profile
            try:
                user_profile = UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                return Response({
                    'error': 'User profile not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check if job exists
            try:
                job = Job.objects.get(id=job_id)
            except Job.DoesNotExist:
                return Response({
                    'error': f'Job with ID {job_id} not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check if user owns this job
            if job.posted_by != request.user:
                return Response({
                    'error': 'You can only edit jobs you posted'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Get job poster's role
            try:
                poster_profile = UserProfile.objects.get(user=job.posted_by)
            except UserProfile.DoesNotExist:
                return Response({
                    'error': 'Job poster profile not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Role-based access control
            if user_profile.role == 'employer' and poster_profile.role != 'employer':
                return Response({
                    'error': 'Employers can only edit employer jobs'
                }, status=status.HTTP_403_FORBIDDEN)
            
            if user_profile.role == 'company' and poster_profile.role != 'company':
                return Response({
                    'error': 'Companies can only edit company jobs'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # User can edit this job, proceed with update
            serializer = JobCreateSerializer(job, data=request.data, partial=True, context={'request': request})
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': 'Job updated successfully',
                    'data': JobSerializer(job).data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': f'Update failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MyJobsAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Get user profile
            try:
                user_profile = UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                return Response({
                    'error': 'User profile not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Filter jobs based on user role
            if user_profile.role == 'employer':
                # Employers see only jobs posted by employers
                employer_users = UserProfile.objects.filter(role='employer').values_list('user_id', flat=True)
                jobs = Job.objects.filter(posted_by__in=employer_users, posted_by=request.user)
            elif user_profile.role == 'company':
                # Companies see only jobs posted by companies
                company_users = UserProfile.objects.filter(role='company').values_list('user_id', flat=True)
                jobs = Job.objects.filter(posted_by__in=company_users, posted_by=request.user)
            else:
                # Employees cannot post jobs, return empty
                jobs = Job.objects.none()
            
            serializer = JobSerializer(jobs, many=True)
            return Response({
                'message': 'Your jobs retrieved successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JobDeleteAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, job_id):
        try:
            # Get user profile
            try:
                user_profile = UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                return Response({
                    'error': 'User profile not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            if user_profile.role == 'employee':
                return Response({
                    'error': 'Employees cannot delete jobs'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Check if job exists
            try:
                job = Job.objects.get(id=job_id)
            except Job.DoesNotExist:
                return Response({
                    'error': f'Job with ID {job_id} not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check if user owns this job
            if job.posted_by != request.user:
                return Response({
                    'error': 'You can only delete jobs you posted'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Get job poster's role
            try:
                poster_profile = UserProfile.objects.get(user=job.posted_by)
            except UserProfile.DoesNotExist:
                return Response({
                    'error': 'Job poster profile not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Role-based access control
            if user_profile.role == 'employer' and poster_profile.role != 'employer':
                return Response({
                    'error': 'Employers can only delete employer jobs'
                }, status=status.HTTP_403_FORBIDDEN)
            
            if user_profile.role == 'company' and poster_profile.role != 'company':
                return Response({
                    'error': 'Companies can only delete company jobs'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Delete the job
            job.delete()
            return Response({
                'message': 'Job deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Delete failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JobSearchAPI(APIView):
    """Advanced job search with multiple filters"""
    
    def get(self, request):
        try:
            jobs = Job.objects.filter(is_active=True)
            
            # Text search across multiple fields
            search = request.query_params.get('search')
            if search and search.strip():  # Check if search is not empty
                from django.db.models import Q
                jobs = jobs.filter(
                    Q(title__icontains=search) |
                    Q(description__icontains=search) |
                    Q(company_name__icontains=search) |
                    Q(skills_required__icontains=search) |
                    Q(location__icontains=search)
                )
            
            # Location filter
            location = request.query_params.get('location')
            if location:
                jobs = jobs.filter(location__icontains=location)
            
            # Job type filter (multiple values supported)
            job_types = request.query_params.getlist('job_type')
            if job_types:
                jobs = jobs.filter(job_type__in=job_types)
            
            # Experience level filter (multiple values supported)
            experience_levels = request.query_params.getlist('experience_level')
            if experience_levels:
                jobs = jobs.filter(experience_level__in=experience_levels)
            
            # Company filter
            company_name = request.query_params.get('company_name')
            if company_name:
                jobs = jobs.filter(company_name__icontains=company_name)
            
            # Salary range filters
            salary_min = request.query_params.get('salary_min')
            if salary_min:
                try:
                    salary_min = float(salary_min)
                    jobs = jobs.filter(salary_max__gte=salary_min)
                except ValueError:
                    pass
            
            salary_max = request.query_params.get('salary_max')
            if salary_max:
                try:
                    salary_max = float(salary_max)
                    jobs = jobs.filter(salary_min__lte=salary_max)
                except ValueError:
                    pass
            
            # Skills filter (comma-separated)
            skills = request.query_params.get('skills')
            if skills:
                skill_list = [skill.strip() for skill in skills.split(',')]
                from django.db.models import Q
                skill_query = Q()
                for skill in skill_list:
                    skill_query |= Q(skills_required__icontains=skill)
                jobs = jobs.filter(skill_query)
            
            # Date range filters
            date_from = request.query_params.get('date_from')
            if date_from:
                try:
                    from datetime import datetime
                    date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                    jobs = jobs.filter(created_at__date__gte=date_from)
                except ValueError:
                    pass
            
            date_to = request.query_params.get('date_to')
            if date_to:
                try:
                    from datetime import datetime
                    date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                    jobs = jobs.filter(created_at__date__lte=date_to)
                except ValueError:
                    pass
            
            # Posted by specific user
            posted_by = request.query_params.get('posted_by')
            if posted_by:
                jobs = jobs.filter(posted_by__username__icontains=posted_by)
            
            # Sorting
            sort_by = request.query_params.get('sort_by', '-created_at')
            valid_sort_fields = [
                'created_at', '-created_at', 'title', '-title', 
                'salary_min', '-salary_min', 'salary_max', '-salary_max',
                'company_name', '-company_name', 'location', '-location'
            ]
            if sort_by in valid_sort_fields:
                jobs = jobs.order_by(sort_by)
            
            # Pagination
            page = int(request.query_params.get('page', 1))
            page_size = min(int(request.query_params.get('page_size', 10)), 50)  # Max 50 per page
            start = (page - 1) * page_size
            end = start + page_size
            
            total_count = jobs.count()
            jobs_page = jobs[start:end]
            
            serializer = JobSerializer(jobs_page, many=True)
            
            return Response({
                'message': 'Jobs search completed successfully',
                'count': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_count + page_size - 1) // page_size,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JobTextSearchAPI(APIView):
    """Simple text search for jobs"""
    
    def get(self, request):
        try:
            search = request.query_params.get('search', '').strip()
            
            if not search:
                return Response({
                    'message': 'Please provide a search term',
                    'count': 0,
                    'data': []
                }, status=status.HTTP_200_OK)
            
            from django.db.models import Q
            jobs = Job.objects.filter(
                is_active=True
            ).filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(company_name__icontains=search) |
                Q(skills_required__icontains=search) |
                Q(location__icontains=search)
            )
            
            serializer = JobSerializer(jobs, many=True)
            return Response({
                'message': f'Search results for "{search}"',
                'count': jobs.count(),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AvailableJobsAPI(APIView):
    """Get jobs available for application (excludes own jobs and already applied jobs)"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.role == 'company':
                return Response({
                    'error': 'Companies cannot apply for jobs'
                }, status=status.HTTP_403_FORBIDDEN)
            
            jobs = Job.objects.filter(is_active=True).exclude(posted_by=request.user)
            
            applied_job_ids = JobApplication.objects.filter(
                applicant=request.user
            ).values_list('job_id', flat=True)
            jobs = jobs.exclude(id__in=applied_job_ids)
            
            serializer = JobSerializer(jobs, many=True)
            jobs_data = serializer.data
            
            for job_data in jobs_data:
                job_data['can_apply'] = True
                job_data['application_status'] = 'not_applied'
            
            return Response({
                'message': 'Available jobs for application retrieved successfully',
                'count': jobs.count(),
                'data': jobs_data
            }, status=status.HTTP_200_OK)
            
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'User profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JobFilterAPI(APIView):
    """Filter jobs by various criteria"""
    
    def get(self, request):
        try:
            jobs = Job.objects.filter(is_active=True)
            
            # Filter by job title
            title = request.query_params.get('title')
            if title:
                jobs = jobs.filter(title__icontains=title)
            
            # Filter by company
            company = request.query_params.get('company')
            if company:
                jobs = jobs.filter(company_name__icontains=company)
            
            # Filter by location
            location = request.query_params.get('location')
            if location:
                jobs = jobs.filter(location__icontains=location)
            
            # Filter by job type (supports multiple values)
            job_type = request.query_params.get('job_type')
            if job_type:
                # Handle comma-separated values
                if ',' in job_type:
                    job_types = [jt.strip() for jt in job_type.split(',')]
                    jobs = jobs.filter(job_type__in=job_types)
                else:
                    jobs = jobs.filter(job_type=job_type)
            
            # Filter by experience level
            experience_level = request.query_params.get('experience_level')
            if experience_level:
                jobs = jobs.filter(experience_level=experience_level)
            
            # Filter by salary range
            salary_min = request.query_params.get('salary_min')
            if salary_min:
                try:
                    salary_min = float(salary_min)
                    jobs = jobs.filter(salary_max__gte=salary_min)
                except ValueError:
                    pass
            
            salary_max = request.query_params.get('salary_max')
            if salary_max:
                try:
                    salary_max = float(salary_max)
                    jobs = jobs.filter(salary_min__lte=salary_max)
                except ValueError:
                    pass
            
            # Sorting
            sort_by = request.query_params.get('sort_by', '-created_at')
            valid_sort_fields = [
                'created_at', '-created_at', 'title', '-title', 
                'salary_min', '-salary_min', 'salary_max', '-salary_max'
            ]
            if sort_by in valid_sort_fields:
                jobs = jobs.order_by(sort_by)
            
            # Pagination
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            start = (page - 1) * page_size
            end = start + page_size
            
            total_count = jobs.count()
            jobs_page = jobs[start:end]
            
            serializer = JobSerializer(jobs_page, many=True)
            
            return Response({
                'message': 'Jobs filtered successfully',
                'count': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_count + page_size - 1) // page_size,
                'filters_applied': {
                    'title': title,
                    'company': company,
                    'location': location,
                    'job_type': job_type,
                    'experience_level': experience_level,
                    'salary_min': salary_min,
                    'salary_max': salary_max
                },
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JobFiltersAPI(APIView):
    """Get available filter options"""
    
    def get(self, request):
        try:
            filter_options = {
                'job_types': [{'value': choice[0], 'label': choice[1]} for choice in Job.JOB_TYPE_CHOICES],
                'experience_levels': [{'value': choice[0], 'label': choice[1]} for choice in Job.EXPERIENCE_CHOICES],
                'locations': [{'value': loc, 'label': loc} for loc in Job.objects.filter(is_active=True).values_list('location', flat=True).distinct()],
                'companies': list(Job.objects.filter(is_active=True).values_list('company_name', flat=True).distinct()),
                'salary_ranges': [
                    {'min': 0, 'max': 50000, 'label': 'Under $50K'},
                    {'min': 50000, 'max': 100000, 'label': '$50K - $100K'},
                    {'min': 100000, 'max': 150000, 'label': '$100K - $150K'},
                    {'min': 150000, 'max': None, 'label': 'Above $150K'}
                ]
            }
            
            return Response({
                'message': 'Filter options retrieved successfully',
                'data': filter_options
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)