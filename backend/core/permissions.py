from rest_framework.permissions import BasePermission
from authentication.models import UserProfile


class IsEmployeeUser(BasePermission):
    """Permission for employee users only"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        try:
            profile = UserProfile.objects.get(user=request.user)
            return profile.role == 'employee'
        except UserProfile.DoesNotExist:
            return False


class IsEmployerOrCompanyUser(BasePermission):
    """Permission for employer or company users only"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        try:
            profile = UserProfile.objects.get(user=request.user)
            return profile.role in ['employer', 'company']
        except UserProfile.DoesNotExist:
            return False


class IsJobOwnerOrReadOnly(BasePermission):
    """Permission to edit job only if user is the job poster"""
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.user.is_authenticated
        
        # Write permissions only for job owner
        return obj.posted_by == request.user


class IsApplicationOwnerOrJobOwner(BasePermission):
    """Permission for application owner or job owner"""
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Application owner can view their own application
        if obj.applicant == request.user:
            return True
        
        # Job owner can view applications for their jobs
        if obj.job.posted_by == request.user:
            return True
        
        return False


class CanUpdateApplicationStatus(BasePermission):
    """Permission to update application status (job owner only)"""
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Only job owner can update application status
        return obj.job.posted_by == request.user