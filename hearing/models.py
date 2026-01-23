from django.db import models
from django.contrib.auth.models import User


class UserRole(models.Model):
    """Model to define user role (Advocate or Client)"""
    ROLE_CHOICES = [
        ('advocate', 'Advocate'),
        ('client', 'Client'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class Hearing(models.Model):
    """Model to store hearing information"""
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('postponed', 'Postponed'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    hearing_date = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    case_number = models.CharField(max_length=100, unique=True)
    
    # Relationships
    advocate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hearings_as_advocate')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hearings_as_client')
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-hearing_date']
    
    def __str__(self):
        return f"Hearing {self.case_number} - {self.title}"


class HearingUpdate(models.Model):
    """Model to store hearing updates from advocate or client"""
    UPDATE_TYPE_CHOICES = [
        ('status', 'Status Update'),
        ('adjournment', 'Adjournment'),
        ('verdict', 'Verdict'),
        ('action_required', 'Action Required'),
        ('document', 'Document Upload'),
        ('note', 'General Note'),
    ]
    
    hearing = models.ForeignKey(Hearing, on_delete=models.CASCADE, related_name='updates')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='hearing_updates')
    
    update_type = models.CharField(max_length=20, choices=UPDATE_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Metadata
    is_important = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Visibility
    visible_to_advocate = models.BooleanField(default=True)
    visible_to_client = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Update: {self.title} - {self.hearing.case_number}"
