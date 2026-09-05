from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import UserProfile
from apps.packages.models import PackageSubscription

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Customer Profile'
    fk_name = 'user'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'get_full_name', 'email', 'get_phone', 'get_whatsapp', 'get_subscription_status', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'profile__phone_number', 'profile__whatsapp_number')

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.email:
            from allauth.account.models import EmailAddress
            EmailAddress.objects.update_or_create(
                user=obj,
                email=obj.email,
                defaults={'verified': True, 'primary': True}
            )

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'

    def get_phone(self, obj):
        return getattr(obj, 'profile', None).phone_number if hasattr(obj, 'profile') else '-'
    get_phone.short_description = 'Phone'

    def get_whatsapp(self, obj):
        return getattr(obj, 'profile', None).whatsapp_number if hasattr(obj, 'profile') else '-'
    get_whatsapp.short_description = 'WhatsApp'

    def get_subscription_status(self, obj):
        active_sub = PackageSubscription.objects.filter(user=obj, status='active').order_by('-activation_date').first()
        if active_sub:
            return format_html('<span style="color: green;"><b>Active:</b> {}</span>', active_sub.package.name)
        
        pending_sub = PackageSubscription.objects.filter(user=obj, status='pending').order_by('-created_at').first()
        if pending_sub:
            from django.utils.safestring import mark_safe
            return mark_safe('<span style="color: orange;"><b>Pending Verification</b></span>')
            
        from django.utils.safestring import mark_safe
        return mark_safe('<span style="color: red;">Inactive</span>')
    get_subscription_status.short_description = 'Subscription Status'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'whatsapp_number', 'join_date')
    search_fields = ('user__username', 'user__email', 'phone_number', 'whatsapp_number')
    list_filter = ('join_date',)
