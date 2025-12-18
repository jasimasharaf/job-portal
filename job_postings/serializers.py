from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Job, JobApplication
from authentication.models import UserProfile


class JobSerializer(serializers.ModelSerializer):
    posted_by_name = serializers.CharField(source='posted_by.get_full_name', read_only=True)
    posted_by_email = serializers.CharField(source='posted_by.email', read_only=True)
    applications_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'description', 'company_name', 'location', 
            'job_type', 'experience_level', 'salary_min', 'salary_max',
            'skills_required', 'is_active', 'created_at', 'updated_at',
            'posted_by_name', 'posted_by_email', 'applications_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_applications_count(self, obj):
        return obj.applications.count()


class JobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'company_name', 'location',
            'job_type', 'experience_level', 'salary_min', 'salary_max',
            'skills_required'
        ]
    
    def validate(self, data):
        user = self.context['request'].user
        try:
            profile = UserProfile.objects.get(user=user)
            if profile.role not in ['employer', 'company']:
                raise serializers.ValidationError("Only employers and companies can post jobs")
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError("User profile not found")
        
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        
        # Auto-set company name for company users
        try:
            profile = UserProfile.objects.get(user=user)
            if profile.role == 'company' and profile.company_name:
                validated_data['company_name'] = profile.company_name
        except UserProfile.DoesNotExist:
            pass
        
        validated_data['posted_by'] = user
        return super().create(validated_data)


class JobApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = [
            'resume', 'cover_letter', 'applicant_phone',
            'expected_salary', 'available_from'
        ]
    
    def validate(self, data):
        user = self.context['request'].user
        job = self.context['job']
        
        # Check if user can apply
        try:
            user_profile = UserProfile.objects.get(user=user)
            if user_profile.role == 'company':
                raise serializers.ValidationError("Companies cannot apply for jobs")
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError("User profile not found")
        
        # Get job poster's profile
        try:
            job_poster_profile = UserProfile.objects.get(user=job.posted_by)
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError("Job poster profile not found")
        
        # Employers cannot apply for their own jobs only
        if user_profile.role == 'employer':
            if job.posted_by == user:
                raise serializers.ValidationError("You cannot apply for your own job")
        
        # Check if already applied
        existing_application = JobApplication.objects.filter(job=job, applicant=user).first()
        if existing_application:
            raise serializers.ValidationError({
                'message': f'You have already applied for this job on {existing_application.applied_at.strftime("%Y-%m-%d %H:%M")}',
                'application_status': existing_application.status,
                'applied_date': existing_application.applied_at,
                'job_title': job.title,
                'company_name': job.company_name
            })
        
        return data
    
    def create(self, validated_data):
        validated_data['applicant'] = self.context['request'].user
        validated_data['job'] = self.context['job']
        return super().create(validated_data)


class JobApplicationListSerializer(serializers.ModelSerializer):
    applicant_name = serializers.CharField(source='applicant.get_full_name', read_only=True)
    applicant_role = serializers.CharField(source='applicant.userprofile.role', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.company_name', read_only=True)
    job_owner_name = serializers.CharField(source='job.posted_by.get_full_name', read_only=True)
    job_owner_email = serializers.CharField(source='job.posted_by.email', read_only=True)
    job_owner_role = serializers.CharField(source='job.posted_by.userprofile.role', read_only=True)
    
    class Meta:
        model = JobApplication
        fields = [
            'id', 'status', 'applied_at', 'applicant_name', 'applicant_role',
            'job_title', 'company_name', 'applicant_phone',
            'expected_salary', 'job_owner_name', 'job_owner_email', 'job_owner_role'
        ]


class JobApplicationReceivedSerializer(serializers.ModelSerializer):
    applicant_name = serializers.CharField(source='applicant.get_full_name', read_only=True)
    applicant_role = serializers.CharField(source='applicant.userprofile.role', read_only=True)
    applicant_email = serializers.CharField(source='applicant.email', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.company_name', read_only=True)
    job_owner_name = serializers.CharField(source='job.posted_by.get_full_name', read_only=True)
    job_owner_email = serializers.CharField(source='job.posted_by.email', read_only=True)
    job_owner_role = serializers.CharField(source='job.posted_by.userprofile.role', read_only=True)
    
    class Meta:
        model = JobApplication
        fields = [
            'id', 'applied_at', 'applicant_name', 'applicant_role',
            'job_title', 'company_name', 'applicant_phone', 'applicant_email',
            'expected_salary', 'job_owner_name', 'job_owner_email', 'job_owner_role',
            'resume', 'cover_letter'
        ]


class JobApplicationDetailSerializer(serializers.ModelSerializer):
    applicant_name = serializers.CharField(source='applicant.get_full_name', read_only=True)
    applicant_role = serializers.CharField(source='applicant.userprofile.role', read_only=True)
    applicant_email = serializers.CharField(source='applicant.email', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    company_name = serializers.CharField(source='job.company_name', read_only=True)
    job_location = serializers.CharField(source='job.location', read_only=True)
    
    class Meta:
        model = JobApplication
        fields = [
            'id', 'status', 'applied_at', 'updated_at',
            'applicant_name', 'applicant_role', 'applicant_email', 'job_title', 'company_name', 'job_location',
            'resume', 'cover_letter'
        ]


class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ['status']
    
    def validate(self, data):
        user = self.context['request'].user
        application = self.instance
        
        # Only job owner can update status
        if application.job.posted_by != user:
            raise serializers.ValidationError("Only job owner can update application status")
        
        return data


class JobSearchSerializer(serializers.Serializer):
    search = serializers.CharField(required=False, help_text="Search in title, description, company")
    location = serializers.CharField(required=False)
    job_type = serializers.ChoiceField(choices=Job.JOB_TYPE_CHOICES, required=False)
    experience_level = serializers.ChoiceField(choices=Job.EXPERIENCE_CHOICES, required=False)
    salary_min = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    salary_max = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    company_name = serializers.CharField(required=False)