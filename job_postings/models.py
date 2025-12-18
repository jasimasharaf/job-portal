from django.db import models
from django.contrib.auth.models import User


class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
    ]
    
    EXPERIENCE_CHOICES = [
        ('entry', 'Entry Level (0-1 years)'),
        ('junior', 'Junior (1-3 years)'),
        ('mid', 'Mid Level (3-5 years)'),
        ('senior', 'Senior (5+ years)'),
    ]
    
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    title = models.CharField(max_length=200)
    description = models.TextField()
    company_name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    skills_required = models.TextField(help_text="Comma-separated skills")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} at {self.company_name}"
    
    @property
    def applications_count(self):
        return self.applications.count()


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('reviewed', 'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    
    # Resume and Cover Letter (Required)
    resume = models.FileField(upload_to='resumes/%Y/%m/', default='resumes/default_resume.pdf')
    cover_letter = models.TextField(default='No cover letter provided')
    
    # Contact Information (Required)
    applicant_phone = models.CharField(max_length=15, default='0000000000')
    applicant_email = models.EmailField(default='noemail@example.com')
    employer_phone = models.CharField(max_length=15, blank=True, null=True)
    employer_email = models.EmailField(blank=True, null=True)
    
    # Additional Info
    expected_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    available_from = models.DateField(blank=True, null=True)
    
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['job', 'applicant']
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.applicant.get_full_name()} applied for {self.job.title}"