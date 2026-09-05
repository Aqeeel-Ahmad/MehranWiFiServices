from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import Complaint

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'user_name', 'phone_number', 'subject', 'status_badge', 'created_at', 'resolved_at')
    list_filter = ('status', 'created_at')
    search_fields = ('ticket_number', 'user_name', 'phone_number', 'subject', 'description', 'user__username')
    readonly_fields = ('ticket_number', 'created_at', 'resolved_at')
    actions = ['mark_in_progress', 'mark_resolved']

    def status_badge(self, obj):
        if obj.status == 'resolved':
            return mark_safe('<span style="background: #10b981; color: white; padding: 3px 8px; border-radius: 12px; font-weight: bold;">🟢 Resolved</span>')
        elif obj.status == 'in_progress':
            return mark_safe('<span style="background: #3b82f6; color: white; padding: 3px 8px; border-radius: 12px; font-weight: bold;">🔵 In Progress</span>')
        elif obj.status == 'pending':
            return mark_safe('<span style="background: #f59e0b; color: white; padding: 3px 8px; border-radius: 12px; font-weight: bold;">🟡 Pending</span>')
        return obj.get_status_display()
    status_badge.short_description = 'Status'

    def mark_in_progress(self, request, queryset):
        queryset.update(status='in_progress')
        self.message_user(request, f"Updated {queryset.count()} complaint(s) to In Progress.")
    mark_in_progress.short_description = "Mark as In Progress"

    def mark_resolved(self, request, queryset):
        queryset.update(status='resolved', resolved_at=timezone.now())
        self.message_user(request, f"Marked {queryset.count()} complaint(s) as Resolved.")
    mark_resolved.short_description = "Mark as Resolved"
