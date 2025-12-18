from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class BaseProfile(models.Model):
    """Abstract base profile with common fields"""
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    class Meta:
        abstract = True


class EmployeeProfile(BaseProfile):
    """Enhanced employee profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    
    # Personal Info
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[
        ('male', 'Male'), ('female', 'Female'), ('other', 'Other')
    ], blank=True, null=True)
    
    # Professional Info
    skills = models.TextField(blank=True, null=True, help_text="Comma-separated skills")
    education = models.TextField(blank=True, null=True)
    experience_years = models.PositiveIntegerField(blank=True, null=True)
    experience_details = models.TextField(blank=True, null=True)
    
    # Career Preferences
    preferred_job_type = models.CharField(max_length=20, choices=[
        ('full_time', 'Full Time'), ('part_time', 'Part Time'),
        ('contract', 'Contract'), ('internship', 'Internship')
    ], blank=True, null=True)
    preferred_location = models.CharField(max_length=200, blank=True, null=True)
    open_to_remote = models.BooleanField(default=True)
    expected_salary_min = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    expected_salary_max = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    # Documents & Media
    resume = models.FileField(upload_to='employee_resumes/%Y/%m/', blank=True, null=True)
    profile_image = models.ImageField(upload_to='employee_images/', blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    
    # Availability
    available_from = models.DateField(blank=True, null=True)
    notice_period = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - Employee Profile"
    
    class Meta:
        db_table = 'employee_profiles'


class EmployerProfile(BaseProfile):
    """Enhanced employer profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer_profile')
    
    # Professional Info
    position = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    company_working_for = models.CharField(max_length=200, blank=True, null=True)
    
    # Hiring Experience
    years_of_hiring_experience = models.PositiveIntegerField(blank=True, null=True)
    specialization_areas = models.TextField(blank=True, null=True, 
                                          help_text="Areas of expertise for hiring")
    
    # Contact & Media
    profile_image = models.ImageField(upload_to='employer_images/', blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    
    # Verification
    is_verified_employer = models.BooleanField(default=False)
    verification_document = models.FileField(upload_to='employer_verification/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - Employer Profile"
    
    class Meta:
        db_table = 'employer_profiles'


class CompanyProfile(BaseProfile):
    """Enhanced company profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    
    # Company Basic Info
    company_name = models.CharField(max_length=200, db_index=True)
    company_description = models.TextField(blank=True, null=True)
    tagline = models.CharField(max_length=200, blank=True, null=True)
    
    # Company Details
    industry = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    company_type = models.CharField(max_length=50, choices=[
        ('startup', 'Startup'), ('small', 'Small Business'),
        ('medium', 'Medium Enterprise'), ('large', 'Large Enterprise'),
        ('nonprofit', 'Non-Profit'), ('government', 'Government')
    ], blank=True, null=True)
    
    company_size = models.CharField(max_length=50, choices=[
        ('1-10', '1-10 employees'), ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'), ('201-500', '201-500 employees'),
        ('501-1000', '501-1000 employees'), ('1000+', '1000+ employees')
    ], blank=True, null=True)
    
    founded_year = models.PositiveIntegerField(blank=True, null=True)
    
    # Contact & Location
    website = models.URLField(blank=True, null=True)
    headquarters_location = models.CharField(max_length=200, blank=True, null=True)
    
    # Social Media & Branding
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='company_covers/', blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    
    # Verification & Legal
    is_verified_company = models.BooleanField(default=False)
    business_registration_number = models.CharField(max_length=100, blank=True, null=True)
    tax_id = models.CharField(max_length=100, blank=True, null=True)
    verification_documents = models.FileField(upload_to='company_verification/', blank=True, null=True)
    
    # Company Culture
    company_values = models.TextField(blank=True, null=True)
    work_culture = models.TextField(blank=True, null=True)
    benefits_offered = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.company_name} - Company Profile"
    
    class Meta:
        db_table = 'company_profiles'
        indexes = [
            models.Index(fields=['company_name', 'industry']),
            models.Index(fields=['is_verified_company']),
        ]


class Post(models.Model):
    """Posts created by users on their profiles"""
    POST_TYPES = [
        ('text', 'Text Post'),
        ('image', 'Image Post'),
        ('achievement', 'Achievement'),
        ('job_update', 'Job Update'),
    ]
    
    # Generic foreign key to link to any profile type
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    profile = GenericForeignKey('content_type', 'object_id')
    
    post_type = models.CharField(max_length=20, choices=POST_TYPES, default='text')
    content = models.TextField()
    image = models.ImageField(upload_to='posts/%Y/%m/', blank=True, null=True)
    
    # Engagement
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    class Meta:
        db_table = 'profile_posts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"Post by {self.profile} - {self.post_type}"


class PostLike(models.Model):
    """Likes on posts"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    class Meta:
        db_table = 'post_likes'
        unique_together = ['post', 'user']


class PostComment(models.Model):
    """Comments on posts"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    class Meta:
        db_table = 'post_comments'
        ordering = ['created_at']