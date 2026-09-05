from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Customer Profile'
    fk_name = 'user'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_phone', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')

    def get_inline_instances(self, request, obj=None):
        # Do not include inlines when adding a new user to prevent ManagementForm validation errors
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

    def get_phone(self, obj):
        return getattr(obj, 'profile', None).phone_number if hasattr(obj, 'profile') else '-'
    get_phone.short_description = 'Phone'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'whatsapp_number', 'join_date')
    search_fields = ('user__username', 'user__email', 'phone_number', 'whatsapp_number')
    list_filter = ('join_date',)
