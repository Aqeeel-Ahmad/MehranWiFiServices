import urllib.parse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Payment
from apps.packages.models import PackageSubscription
from .pdf_generator import generate_receipt_pdf, generate_history_pdf

@login_required
def receipt_view(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    # Ensure customer can only view their own receipt unless staff
    if payment.user != request.user and not request.user.is_staff:
        messages.error(request, "Access denied. You cannot view receipts belonging to other accounts.")
        return redirect('dashboard')

    sub = payment.subscription
    pkg_name = sub.package_name_snapshot if sub else (sub.package.name if sub and sub.package else "Fiber Internet")
    speed = sub.speed_snapshot if sub else (sub.package.speed_mbps if sub and sub.package else "N/A")
    expiry_date_str = sub.expiry_date.strftime('%B 08, %Y') if sub and sub.expiry_date else "N/A"
    purchase_date_str = sub.purchase_date.strftime('%B %d, %Y') if sub and sub.purchase_date else payment.payment_date.strftime('%B %d, %Y')

    # Prepare WhatsApp message template
    wa_message = (
        f"📄 *MEHRAN WIFI SERVICE - DIGITAL RECEIPT*\n"
        f"Receipt #: {payment.receipt_number}\n"
        f"Customer: {payment.user.get_full_name() or payment.user.username} (ID: #{payment.user.id})\n"
        f"Package: {pkg_name} ({speed} Mbps)\n"
        f"Price: Rs. {payment.amount:,.0f}\n"
        f"Purchase Date: {purchase_date_str}\n"
        f"Expiry Date: {expiry_date_str}\n"
        f"Payment Method: EasyPaisa ({payment.easypaisa_number})\n"
        f"TRX ID: {payment.transaction_id}\n"
        f"Status: {payment.get_verification_status_display()}\n"
        f"Thank you for choosing Mehran WiFi Service! Hotline: 03454524086"
    )
    wa_encoded = urllib.parse.quote(wa_message)
    user_phone = getattr(payment.user.profile, 'whatsapp_number', None) or getattr(payment.user.profile, 'phone_number', '')
    # Clean phone number for WhatsApp link
    clean_phone = "".join(filter(str.isdigit, user_phone))
    if clean_phone.startswith('0'):
        clean_phone = '92' + clean_phone[1:]

    wa_url = f"https://api.whatsapp.com/send?phone={clean_phone}&text={wa_encoded}" if clean_phone else f"https://api.whatsapp.com/send?text={wa_encoded}"

    context = {
        'payment': payment,
        'subscription': sub,
        'pkg_name': pkg_name,
        'speed': speed,
        'purchase_date_str': purchase_date_str,
        'expiry_date_str': expiry_date_str,
        'wa_url': wa_url,
    }
    return render(request, 'payments/receipt.html', context)


@login_required
def download_receipt_pdf_view(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    if payment.user != request.user and not request.user.is_staff:
        messages.error(request, "Unauthorized to download this receipt.")
        return redirect('dashboard')

    pdf_data = generate_receipt_pdf(payment)
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="MehranWiFi_Receipt_{payment.receipt_number}.pdf"'
    return response


@login_required
def send_receipt_email_view(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    if payment.user != request.user and not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

    recipient_email = payment.user.email
    if not recipient_email:
        return JsonResponse({'status': 'error', 'message': 'No registered email found for your account.'}, status=400)

    sub = payment.subscription
    pkg_name = sub.package_name_snapshot if sub else "Fiber Internet"
    speed = sub.speed_snapshot if sub else "N/A"
    expiry_str = sub.expiry_date.strftime('%B %d, %Y') if sub and sub.expiry_date else "8th of next month"

    subject = f"Mehran WiFi Service - Payment Receipt #{payment.receipt_number}"
    body = f"""Dear {payment.user.get_full_name() or payment.user.username},

Thank you for your payment to Mehran WiFi Service.

Here are your payment and subscription details:
--------------------------------------------------
Receipt Number : {payment.receipt_number}
Package        : {pkg_name} ({speed} Mbps)
Amount         : Rs. {payment.amount:,.0f}
Method         : EasyPaisa ({payment.easypaisa_number})
Transaction ID : {payment.transaction_id}
Purchase Date  : {payment.payment_date.strftime('%B %d, %Y %H:%M')}
Expiry Date    : {expiry_str}
Payment Status : {payment.get_verification_status_display()}
--------------------------------------------------

If your payment is pending verification, our team will activate your package shortly.
For support, call or WhatsApp: 03454524086.

Warm regards,
Mehran WiFi Service Team
support@mehranwifi.com
"""

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        return JsonResponse({'status': 'success', 'message': f'Receipt successfully sent to {recipient_email}.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Could not send email: {str(e)}'}, status=500)


@login_required
def track_view(request):
    user = request.user
    subscriptions = PackageSubscription.objects.filter(user=user).select_related('package', 'payment')
    total_packages = subscriptions.count()
    total_spent = sum(s.price_snapshot for s in subscriptions.filter(status__in=['active', 'expired']))

    # Active subscription
    active_sub = subscriptions.filter(status='active').first()

    context = {
        'user': user,
        'profile': getattr(user, 'profile', None),
        'subscriptions': subscriptions,
        'total_packages': total_packages,
        'total_spent': total_spent,
        'active_sub': active_sub,
    }
    return render(request, 'payments/track.html', context)


@login_required
def download_history_pdf_view(request):
    user = request.user
    subscriptions = PackageSubscription.objects.filter(user=user).select_related('package')
    if not subscriptions.exists():
        messages.warning(request, "No package history available to download.")
        return redirect('track')

    pdf_data = generate_history_pdf(user, subscriptions)
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="MehranWiFi_AccountHistory_{user.username}.pdf"'
    return response
