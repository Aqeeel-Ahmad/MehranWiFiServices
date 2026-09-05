from django.conf import settings

def site_settings(request):
    unread_count = 0
    active_sub = None
    if request.user.is_authenticated:
        try:
            from apps.notifications.models import Notification
            unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        except Exception:
            unread_count = 0
            
        try:
            from apps.packages.models import PackageSubscription
            active_sub = PackageSubscription.objects.filter(
                user=request.user,
                status='active'
            ).order_by('-activation_date').first()
        except Exception:
            active_sub = None

    return {
        'ISP_NAME': getattr(settings, 'ISP_NAME', 'MEHRAN WIFI SERVICE'),
        'ISP_TAGLINE': getattr(settings, 'ISP_TAGLINE', 'Fast, Reliable & Unlimited Fiber Internet'),
        'ISP_PHONE': getattr(settings, 'ISP_PHONE', '03454524086'),
        'ISP_EMAIL': getattr(settings, 'ISP_EMAIL', 'support@mehranwifi.com'),
        'ISP_ADDRESS': getattr(settings, 'ISP_ADDRESS', 'Main Optical Fiber Hub, Mehran City, Pakistan'),
        'EASYPAISA_NUMBER': getattr(settings, 'EASYPAISA_NUMBER', '03454524086'),
        'EASYPAISA_ACCOUNT_NAME': getattr(settings, 'EASYPAISA_ACCOUNT_NAME', 'Mehran WiFi Service'),
        'unread_notifications_count': unread_count,
        'user_active_subscription': active_sub,
    }
