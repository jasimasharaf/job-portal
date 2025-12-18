from django.db import models
from django.contrib.auth.models import User
from authentication.models import UserProfile


class Follow(models.Model):
    """Follow relationship between users with role-based rules"""
    
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['follower', 'following']
        indexes = [
            models.Index(fields=['follower', 'created_at']),
            models.Index(fields=['following', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.follower.get_full_name()} follows {self.following.get_full_name()}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Prevent self-following
        if self.follower == self.following:
            raise ValidationError("Users cannot follow themselves")
        
        # Role-based validation
        try:
            follower_profile = UserProfile.objects.get(user=self.follower)
            following_profile = UserProfile.objects.get(user=self.following)
            
            # Companies can only follow other companies
            if follower_profile.role == 'company' and following_profile.role != 'company':
                raise ValidationError("Companies can only follow other companies")
                
        except UserProfile.DoesNotExist:
            raise ValidationError("User profile not found")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class FollowRequest(models.Model):
    """Optional: For private accounts (future feature)"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_follow_requests')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_follow_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['from_user', 'to_user']
    
    def __str__(self):
        return f"{self.from_user.get_full_name()} -> {self.to_user.get_full_name()} ({self.status})"