import urllib.parse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Payment
from apps.packages.models import PackageSubscription
from apps.notifications.models import Notification
from .pdf_generator import generate_receipt_pdf, generate_history_pdf

@login_required
def easypaisa_gateway_view(request, subscription_id):
    subscription = get_object_or_404(PackageSubscription, id=subscription_id)
    if subscription.user != request.user and not request.user.is_staff:
        messages.error(request, "Unauthorized access to subscription.")
        return redirect('dashboard')

    context = {
        'subscription': subscription,
        'easypaisa_number': '03452524086',
        'easypaisa_account_name': 'HAM 3 NETWORK',
        'amount': subscription.price_snapshot,
        'pkg_name': subscription.package_name_snapshot or (subscription.package.name if subscription.package else "Fiber Plan"),
        'speed': subscription.speed_snapshot or (subscription.package.speed_mbps if subscription.package else ""),
    }
    return render(request, 'payments/easypaisa_gateway.html', context)


@login_required
def activate_package_view(request, subscription_id):
    subscription = get_object_or_404(PackageSubscription, id=subscription_id)
    if subscription.user != request.user and not request.user.is_staff:
        messages.error(request, "Unauthorized access to subscription.")
        return redirect('dashboard')

    if request.method == 'POST':
        sender_number = request.POST.get('sender_number', '').strip()
        transaction_id = request.POST.get('transaction_id', '').strip()
        screenshot = request.FILES.get('payment_screenshot')

        if not transaction_id:
            messages.error(request, "Please provide the EasyPaisa Transaction ID (TRX ID).")
            return redirect('activate_package', subscription_id=subscription.id)

        # Check if payment record already exists for this subscription
        payment = Payment.objects.filter(subscription=subscription).first()
        if not payment:
            payment = Payment.objects.create(
                user=request.user,
                subscription=subscription,
                amount=subscription.price_snapshot,
                payment_method='EasyPaisa',
                easypaisa_number='03452524086',
                sender_number=sender_number or getattr(request.user.profile, 'phone_number', ''),
                transaction_id=transaction_id,
                payment_screenshot=screenshot,
                payment_date=timezone.now(),
                verification_status='pending'
            )
        else:
            payment.sender_number = sender_number
            payment.transaction_id = transaction_id
            if screenshot:
                payment.payment_screenshot = screenshot
            payment.verification_status = 'pending'
            payment.save()

        # In-app notification
        pkg_name = subscription.package_name_snapshot or "Fiber Internet"
        Notification.objects.create(
            user=request.user,
            title="🟡 Package Activation in Progress",
            message=f"We received your EasyPaisa payment (TRX: {transaction_id}) for {pkg_name}. Your package is being activated. Please wait.",
            link=f"/payments/receipt/{payment.id}/"
        )

        messages.info(request, "Your package is being activated. Please wait.")
        return redirect('view_receipt', payment_id=payment.id)

    context = {
        'subscription': subscription,
        'easypaisa_number': '03452524086',
        'easypaisa_account_name': 'HAM 3 NETWORK',
        'amount': subscription.price_snapshot,
        'pkg_name': subscription.package_name_snapshot or (subscription.package.name if subscription.package else "Fiber Plan"),
        'speed': subscription.speed_snapshot or (subscription.package.speed_mbps if subscription.package else ""),
        'default_sender_number': getattr(request.user.profile, 'phone_number', '') if hasattr(request.user, 'profile') else '',
    }
    return render(request, 'payments/activate_package.html', context)


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

    # Admin WhatsApp message for direct verification
    admin_wa_phone = '923452524086'
    admin_wa_message = (
        f"🟢 *HAM 3 NETWORK - PAYMENT PROOF*\n"
        f"Receipt #: {payment.receipt_number}\n"
        f"Customer: {payment.user.get_full_name() or payment.user.username} (ID: #{payment.user.id})\n"
        f"Package: {pkg_name} ({speed} Mbps)\n"
        f"Amount: Rs. {payment.amount:,.0f}\n"
        f"EasyPaisa Number: 03452524086\n"
        f"TRX ID: {payment.transaction_id}\n"
        f"Sender Number: {payment.sender_number}\n"
        f"Status: Your package is being activated. Please wait.\n\n"
        f"Assalam o Alaikum! I have submitted my EasyPaisa payment. Please verify and activate my fiber package."
    )
    admin_wa_url = f"https://wa.me/{admin_wa_phone}?text={urllib.parse.quote(admin_wa_message)}"

    # Customer WhatsApp share message
    wa_message = (
        f"📄 *HAM 3 NETWORK - DIGITAL RECEIPT*\n"
        f"Receipt #: {payment.receipt_number}\n"
        f"Customer: {payment.user.get_full_name() or payment.user.username}\n"
        f"Package: {pkg_name} ({speed} Mbps)\n"
        f"Price: Rs. {payment.amount:,.0f}\n"
        f"Purchase Date: {purchase_date_str}\n"
        f"Expiry Date: {expiry_date_str}\n"
        f"TRX ID: {payment.transaction_id}\n"
        f"Status: {payment.get_verification_status_display()}\n"
        f"HAM 3 NETWORK Hotline: 03452524086"
    )
    wa_encoded = urllib.parse.quote(wa_message)
    user_phone = getattr(payment.user.profile, 'whatsapp_number', None) or getattr(payment.user.profile, 'phone_number', '')
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
        'admin_wa_url': admin_wa_url,
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
    response['Content-Disposition'] = f'attachment; filename="HAM 3WiFi_Receipt_{payment.receipt_number}.pdf"'
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

    subject = f"HAM 3 NETWORK - Payment Receipt #{payment.receipt_number}"
    body = f"""Dear {payment.user.get_full_name() or payment.user.username},

Thank you for your payment to HAM 3 NETWORK.

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
For support, call or WhatsApp: 03452524086.

Warm regards,
HAM 3 NETWORK Team
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
    response['Content-Disposition'] = f'attachment; filename="HAM 3WiFi_AccountHistory_{user.username}.pdf"'
    return response
