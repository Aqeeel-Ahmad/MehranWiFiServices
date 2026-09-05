from django.db import models
from django.contrib.auth.models import User
from apps.packages.models import InternetPackage

class SpecialOffer(models.Model):
    title = models.CharField(max_length=150, help_text="Offer Headline, e.g. Free Optical Fiber Installation")
    subtitle = models.CharField(max_length=200, blank=True, help_text="Short subtext")
    discount_tag = models.CharField(max_length=50, default="SPECIAL OFFER", help_text="e.g. 20% OFF, FREE ROUTER")
    description = models.TextField(help_text="Offer terms or description")
    target_package = models.ForeignKey(
        InternetPackage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='special_offers'
    )
    is_active = models.BooleanField(default=True)
    valid_until = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.discount_tag}: {self.title}"


class Feedback(models.Model):
    RATING_CHOICES = [
        (5, '⭐⭐⭐⭐⭐ 5 - Excellent'),
        (4, '⭐⭐⭐⭐ 4 - Very Good'),
        (3, '⭐⭐⭐ 3 - Good'),
        (2, '⭐⭐ 2 - Fair'),
        (1, '⭐ 1 - Poor'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedbacks')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=5)
    message = models.TextField()
    is_approved = models.BooleanField(default=True, help_text="Show on website home page")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.rating} Stars"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"
