import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


def calculate_expiry_date(purchase_date):
    """
    Expiry date is automatically calculated as the 8th of the next calendar month.
    e.g., September 15 -> October 8.
    """
    if isinstance(purchase_date, datetime.datetime):
        purchase_date = purchase_date.date()
    
    if purchase_date.month == 12:
        next_year = purchase_date.year + 1
        next_month = 1
    else:
        next_year = purchase_date.year
        next_month = purchase_date.month + 1
    return datetime.date(next_year, next_month, 8)


from decimal import Decimal

def calculate_custom_price(speed_mbps):
    """
    Calculates monthly price for custom bandwidth between 2 Mbps and 30 Mbps.
    Base Rs. 400 + Rs. 80 per Mbps:
    2 Mbps = Rs. 560, 10 Mbps = Rs. 1,200, 20 Mbps = Rs. 2,000, 30 Mbps = Rs. 2,800.
    """
    speed = max(2, min(30, int(speed_mbps)))
    return Decimal(400 + (speed * 80))


class InternetPackage(models.Model):
    name = models.CharField(max_length=100, help_text="e.g. 20 Mbps Fiber Pro")
    speed_mbps = models.PositiveIntegerField(help_text="Speed in Mbps / MB")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in PKR")
    description = models.TextField(help_text="Short description of the package")
    features = models.TextField(
        blank=True,
        help_text="Enter features separated by newlines (e.g. Unlimited Data, Zero Buffer 4K Streaming, 24/7 Fiber Support)"
    )
    is_featured = models.BooleanField(default=False, help_text="Highlight as Best Value / Most Popular")
    is_custom = models.BooleanField(default=False, help_text="Customizable package (2 to 30 Mbps)")
    is_active = models.BooleanField(default=True, help_text="Available for purchase on website")
    display_order = models.PositiveIntegerField(default=0, help_text="Display sorting order")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'speed_mbps']

    def __str__(self):
        return f"{self.name} ({self.speed_mbps} Mbps) - Rs. {self.price:,.0f}"

    def get_features_list(self):
        if not self.features:
            return []
        return [f.strip() for f in self.features.splitlines() if f.strip()]


class PackageSubscription(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('active', 'Package Activated'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    package = models.ForeignKey(InternetPackage, on_delete=models.SET_NULL, null=True, related_name='subscriptions')
    package_name_snapshot = models.CharField(max_length=100, blank=True)
    speed_snapshot = models.PositiveIntegerField(default=0)
    price_snapshot = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    purchase_date = models.DateField(default=datetime.date.today)
    activation_date = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.package_name_snapshot or self.package} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if self.package and not self.package_name_snapshot:
            self.package_name_snapshot = self.package.name
            self.speed_snapshot = self.package.speed_mbps
            self.price_snapshot = self.package.price

        if not self.expiry_date and self.purchase_date:
            self.expiry_date = calculate_expiry_date(self.purchase_date)

        super().save(*args, **kwargs)

    @property
    def is_active_status(self):
        if self.status != 'active':
            return False
        if self.expiry_date:
            return self.expiry_date >= timezone.localdate()
        return True

    @property
    def remaining_days(self):
        if not self.expiry_date:
            return 0
        today = timezone.localdate()
        delta = (self.expiry_date - today).days
        return max(0, delta)
