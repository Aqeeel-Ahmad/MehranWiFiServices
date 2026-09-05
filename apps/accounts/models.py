from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20, help_text="Registered phone number for connectivity and alerts")
    whatsapp_number = models.CharField(max_length=20, blank=True, help_text="WhatsApp number for digital receipt and updates")
    address = models.TextField(blank=True, help_text="Installation / Customer address")
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    join_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.phone_number or 'No Phone'}"

    @property
    def full_name_or_username(self):
        full = f"{self.user.first_name} {self.user.last_name}".strip()
        return full if full else self.user.username


from allauth.account.models import EmailAddress

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
