from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import InternetPackage, PackageSubscription

@admin.register(InternetPackage)
class InternetPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'speed_badge', 'price_display', 'is_custom', 'is_featured', 'is_active', 'display_order')
    list_editable = ('is_custom', 'is_featured', 'is_active', 'display_order')
    list_filter = ('is_custom', 'is_active', 'is_featured')
    search_fields = ('name', 'description')

    def speed_badge(self, obj):
        return format_html('<span style="background: #0284c7; color: white; padding: 3px 8px; border-radius: 12px; font-weight: bold;">⚡ {} Mbps</span>', obj.speed_mbps)
    speed_badge.short_description = 'Speed'

    def price_display(self, obj):
        price_str = f"Rs. {obj.price:,.0f}"
        return format_html('<b>{}</b>', price_str)
    price_display.short_description = 'Monthly Price'


@admin.register(PackageSubscription)
class PackageSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user_link', 'package_display', 'speed_display', 'price_display',
        'purchase_date', 'expiry_date', 'status_badge', 'remaining_days_display'
    )
    list_filter = ('status', 'purchase_date', 'expiry_date')
    search_fields = ('user__username', 'user__email', 'package_name_snapshot', 'user__profile__phone_number')
    date_hierarchy = 'purchase_date'
    actions = ['activate_selected_subscriptions', 'expire_selected_subscriptions']

    def user_link(self, obj):
        phone = getattr(obj.user, 'profile', None).phone_number if hasattr(obj.user, 'profile') else ''
        return format_html('<b>{}</b><br/><small style="color:#64748b;">{}</small>', obj.user.username, phone)
    user_link.short_description = 'Subscriber'

    def package_display(self, obj):
        return obj.package_name_snapshot or (obj.package.name if obj.package else "N/A")
    package_display.short_description = 'Package'

    def speed_display(self, obj):
        speed = obj.speed_snapshot or (obj.package.speed_mbps if obj.package else '-')
        return f"{speed} Mbps"
    speed_display.short_description = 'Speed'

    def price_display(self, obj):
        return f"Rs. {obj.price_snapshot:,.0f}"
    price_display.short_description = 'Price'

    def status_badge(self, obj):
        if obj.status == 'active':
            return mark_safe('<span style="background: #10b981; color: white; padding: 3px 8px; border-radius: 12px; font-weight: bold;">🟢 Active</span>')
        elif obj.status == 'pending':
            return mark_safe('<span style="background: #f59e0b; color: white; padding: 3px 8px; border-radius: 12px; font-weight: bold;">🟡 Pending</span>')
        elif obj.status == 'expired':
            return mark_safe('<span style="background: #64748b; color: white; padding: 3px 8px; border-radius: 12px; font-weight: bold;">⚪ Expired</span>')
        return obj.get_status_display()
    status_badge.short_description = 'Status'

    def remaining_days_display(self, obj):
        if obj.status == 'active':
            return format_html('<b>{} days</b>', obj.remaining_days)
        return '-'
    remaining_days_display.short_description = 'Remaining'

    def activate_selected_subscriptions(self, request, queryset):
        from django.utils import timezone
        for sub in queryset:
            sub.status = 'active'
            sub.activation_date = timezone.now()
            sub.save()
        self.message_user(request, f"Successfully activated {queryset.count()} subscription(s).")
    activate_selected_subscriptions.short_description = "Activate Selected Subscriptions"

    def expire_selected_subscriptions(self, request, queryset):
        queryset.update(status='expired')
        self.message_user(request, f"Marked {queryset.count()} subscription(s) as expired.")
    expire_selected_subscriptions.short_description = "Expire Selected Subscriptions"
