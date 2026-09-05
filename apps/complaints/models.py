import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Complaint(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('in_progress', 'In Progress / Tech Assigned'),
        ('resolved', 'Resolved'),
    ]

    ticket_number = models.CharField(max_length=50, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints')
    user_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, help_text="Registered contact phone number")
    subject = models.CharField(max_length=200, help_text="Subject / Category of complaint (e.g., Red LOS Light, Slow Speed, Router Issue)")
    description = models.TextField(help_text="Detailed description of the issue")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_response = models.TextField(blank=True, help_text="Resolution details / technician note")
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Ticket #{self.ticket_number or self.id} - {self.subject} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            year_month = timezone.now().strftime('%y%m')
            unique_part = uuid.uuid4().hex[:5].upper()
            self.ticket_number = f"TKT-{year_month}-{unique_part}"
        if self.status == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        super().save(*args, **kwargs)
