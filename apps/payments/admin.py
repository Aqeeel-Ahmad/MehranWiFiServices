from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'receipt_number', 'user_link', 'package_info', 'amount_display',
        'transaction_id_display', 'screenshot_thumb', 'verification_status_badge',
        'payment_date', 'quick_actions'
    )
    list_filter = ('verification_status', 'payment_date', 'payment_method')
    search_fields = (
        'receipt_number', 'transaction_id', 'sender_number',
        'user__username', 'user__email', 'user__profile__phone_number'
    )
    readonly_fields = ('receipt_number', 'payment_date', 'verified_at', 'verified_by', 'screenshot_preview')
    actions = ['verify_and_activate_payments', 'mark_payments_rejected']
    date_hierarchy = 'payment_date'

    fieldsets = (
        ('Receipt & Customer', {
            'fields': ('receipt_number', 'user', 'subscription', 'verification_status')
        }),
        ('Payment Gateway Details', {
            'fields': ('payment_method', 'easypaisa_number', 'sender_number', 'transaction_id', 'amount', 'payment_date')
        }),
        ('Proof of Payment', {
            'fields': ('payment_screenshot', 'screenshot_preview')
        }),
        ('Admin Verification Audit', {
            'fields': ('verified_by', 'verified_at', 'admin_notes')
        }),
    )

    def user_link(self, obj):
        phone = getattr(obj.user, 'profile', None).phone_number if hasattr(obj.user, 'profile') else ''
        return format_html('<b>{}</b><br/><small style="color:#64748b;">{}</small>', obj.user.username, phone)
    user_link.short_description = 'Customer'

    def package_info(self, obj):
        if obj.subscription:
            pkg_name = obj.subscription.package_name_snapshot or (obj.subscription.package.name if obj.subscription.package else "Fiber Plan")
            speed = obj.subscription.speed_snapshot or (obj.subscription.package.speed_mbps if obj.subscription.package else "")
            return format_html('<b>{}</b><br/><small style="color:#0284c7;">⚡ {} Mbps</small>', pkg_name, speed)
        return '-'
    package_info.short_description = 'Package'

    def amount_display(self, obj):
        amt_str = f"Rs. {obj.amount:,.0f}"
        return format_html('<b>{}</b>', amt_str)
    amount_display.short_description = 'Amount'

    def transaction_id_display(self, obj):
        return format_html('<code style="background:#e0f2fe; color:#0369a1; padding:2px 6px; border-radius:4px; font-weight:bold;">{}</code>', obj.transaction_id)
    transaction_id_display.short_description = 'EasyPaisa TRX'

    def screenshot_thumb(self, obj):
        if obj.payment_screenshot:
            return format_html('<a href="{}" target="_blank"><img src="{}" style="width: 45px; height: 45px; object-fit: cover; border-radius: 6px; border: 1px solid #cbd5e1;"/></a>', obj.payment_screenshot.url, obj.payment_screenshot.url)
        return mark_safe('<span style="color:#94a3b8; font-size:11px;">No Proof</span>')
    screenshot_thumb.short_description = 'Screenshot'

    def screenshot_preview(self, obj):
        if obj.payment_screenshot:
            return format_html('<a href="{}" target="_blank"><img src="{}" style="max-width: 400px; max-height: 400px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"/></a><br/><small>Click image to open full size in new tab</small>', obj.payment_screenshot.url, obj.payment_screenshot.url)
        return "No screenshot uploaded."
    screenshot_preview.short_description = 'Payment Screenshot Preview'

    def verification_status_badge(self, obj):
        if obj.verification_status == 'verified':
            return mark_safe('<span style="background: #10b981; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size:11px;">🟢 Verified & Active</span>')
        elif obj.verification_status == 'pending':
            return mark_safe('<span style="background: #f59e0b; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size:11px;">🟡 Pending Verification</span>')
        elif obj.verification_status == 'rejected':
            return mark_safe('<span style="background: #ef4444; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size:11px;">🔴 Rejected</span>')
        return obj.get_verification_status_display()
    verification_status_badge.short_description = 'Status'

    def quick_actions(self, obj):
        receipt_url = reverse('download_receipt_pdf', args=[obj.id])
        actions_html = f'<a href="{receipt_url}" class="button" style="background:#0284c7; color:white; padding:3px 8px; font-size:11px; border-radius:4px; text-decoration:none; margin-right:4px;">📄 PDF</a>'
        return mark_safe(actions_html)
    quick_actions.short_description = 'Receipt'

    def verify_and_activate_payments(self, request, queryset):
        count = 0
        for payment in queryset:
            payment.verify_and_activate(admin_user=request.user)
            count += 1
        self.message_user(request, f"Successfully verified {count} payment(s) and activated subscriber package(s)!")
    verify_and_activate_payments.short_description = "🟢 Verify Payment & Activate Package"

    def mark_payments_rejected(self, request, queryset):
        queryset.update(verification_status='rejected')
        for p in queryset:
            if p.subscription:
                p.subscription.status = 'cancelled'
                p.subscription.save()
        self.message_user(request, f"Marked {queryset.count()} payment(s) as rejected.")
    mark_payments_rejected.short_description = "🔴 Reject Selected Payments"
