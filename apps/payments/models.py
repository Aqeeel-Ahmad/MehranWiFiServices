import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.packages.models import PackageSubscription

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified & Activated'),
        ('rejected', 'Rejected'),
    ]

    receipt_number = models.CharField(max_length=50, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    subscription = models.OneToOneField(
        PackageSubscription,
        on_delete=models.CASCADE,
        related_name='payment',
        null=True,
        blank=True
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Payment amount in PKR")
    payment_method = models.CharField(max_length=50, default='EasyPaisa')
    easypaisa_number = models.CharField(max_length=20, default='03454524086')
    sender_number = models.CharField(max_length=20, blank=True, help_text="Customer EasyPaisa sender phone number")
    transaction_id = models.CharField(max_length=100, help_text="EasyPaisa Transaction ID (TRX ID)")
    payment_screenshot = models.ImageField(upload_to='payments/screenshots/', blank=True, null=True)
    payment_date = models.DateTimeField(default=timezone.now)

    verification_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_payments')
    verified_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True, help_text="Internal notes or reason for rejection")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Receipt #{self.receipt_number or self.id} - {self.user.username} - Rs. {self.amount:,.0f} ({self.get_verification_status_display()})"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            prefix = timezone.now().strftime('%Y%m')
            unique_part = uuid.uuid4().hex[:6].upper()
            self.receipt_number = f"MWS-{prefix}-{unique_part}"
        super().save(*args, **kwargs)

    def verify_and_activate(self, admin_user=None):
        """
        Marks payment as verified, activates corresponding subscription,
        sets activation_date, and sends in-app notification.
        """
        self.verification_status = 'verified'
        self.verified_at = timezone.now()
        if admin_user:
            self.verified_by = admin_user
        self.save()

        if self.subscription:
            # Set older active subscriptions of this user to expired
            PackageSubscription.objects.filter(
                user=self.user,
                status='active'
            ).exclude(id=self.subscription.id).update(status='expired')

            self.subscription.status = 'active'
            self.subscription.activation_date = timezone.now()
            self.subscription.save()

            # Create in-app notification for the user
            try:
                from apps.notifications.models import Notification
                pkg_name = self.subscription.package_name_snapshot or (self.subscription.package.name if self.subscription.package else "Fiber Internet")
                speed = self.subscription.speed_snapshot or (self.subscription.package.speed_mbps if self.subscription.package else "")
                expiry_str = self.subscription.expiry_date.strftime('%B %d, %Y') if self.subscription.expiry_date else "N/A"
                
                Notification.objects.create(
                    user=self.user,
                    title="🟢 Package Activated!",
                    message=f"Congratulations! Your {pkg_name} ({speed} Mbps) has been verified and activated. It is valid until {expiry_str}.",
                    link="/dashboard/"
                )
            except Exception:
                pass

        return True
