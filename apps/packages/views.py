import datetime
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import InternetPackage, PackageSubscription, calculate_expiry_date, calculate_custom_price
from apps.payments.models import Payment
from apps.notifications.models import Notification

def package_list_view(request):
    packages = InternetPackage.objects.filter(is_active=True).order_by('display_order', 'speed_mbps')
    active_subscription = None
    if request.user.is_authenticated:
        active_subscription = PackageSubscription.objects.filter(
            user=request.user,
            status='active'
        ).first()

    return render(request, 'packages/package_list.html', {
        'packages': packages,
        'active_subscription': active_subscription,
    })


@login_required
def order_package_wizard_view(request):
    packages = InternetPackage.objects.filter(is_active=True).order_by('display_order', 'speed_mbps')
    selected_pkg_id = request.GET.get('package_id')
    preselected_package = None
    if selected_pkg_id:
        preselected_package = packages.filter(id=selected_pkg_id).first()

    # Preselected custom speed (2 to 30 Mbps)
    preselected_custom_speed = 10
    if request.GET.get('custom_speed'):
        try:
            preselected_custom_speed = max(2, min(30, int(request.GET.get('custom_speed'))))
        except (ValueError, TypeError):
            preselected_custom_speed = 10

    preselected_custom_price = calculate_custom_price(preselected_custom_speed)
    initial_pkg = preselected_package or (packages.first() if packages.exists() else None)
    initial_is_custom = initial_pkg.is_custom if initial_pkg else False
    initial_name = f"Custom {preselected_custom_speed} Mbps Fiber Plan" if initial_is_custom else (initial_pkg.name if initial_pkg else '')
    initial_speed = preselected_custom_speed if initial_is_custom else (initial_pkg.speed_mbps if initial_pkg else 0)
    initial_price = preselected_custom_price if initial_is_custom else (initial_pkg.price if initial_pkg else 0)

    today_str = datetime.date.today().strftime('%Y-%m-%d')
    default_expiry = calculate_expiry_date(datetime.date.today()).strftime('%Y-%m-%d')
    default_expiry_formatted = calculate_expiry_date(datetime.date.today()).strftime('%B 08, %Y')

    if request.method == 'POST':
        package_id = request.POST.get('package_id')
        purchase_date_str = request.POST.get('purchase_date', today_str)
        sender_number = request.POST.get('sender_number', '').strip()
        transaction_id = request.POST.get('transaction_id', '').strip()
        screenshot = request.FILES.get('payment_screenshot')
        custom_speed_input = request.POST.get('custom_speed')

        # Parse date
        try:
            p_date = datetime.datetime.strptime(purchase_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            p_date = datetime.date.today()

        package = get_object_or_404(InternetPackage, id=package_id)
        expiry_date = calculate_expiry_date(p_date)

        if not transaction_id:
            messages.error(request, "Please enter your EasyPaisa Transaction ID (TRX ID).")
            return redirect('order_package')

        # Custom Speed calculation if package is custom
        if package.is_custom:
            try:
                chosen_speed = max(2, min(30, int(custom_speed_input or 10)))
            except (ValueError, TypeError):
                chosen_speed = 10
            pkg_name = f"Custom {chosen_speed} Mbps Fiber Plan"
            pkg_speed = chosen_speed
            pkg_price = calculate_custom_price(chosen_speed)
        else:
            pkg_name = package.name
            pkg_speed = package.speed_mbps
            pkg_price = package.price

        # Create Pending Subscription
        subscription = PackageSubscription.objects.create(
            user=request.user,
            package=package,
            package_name_snapshot=pkg_name,
            speed_snapshot=pkg_speed,
            price_snapshot=pkg_price,
            purchase_date=p_date,
            expiry_date=expiry_date,
            status='pending'
        )

        # Create Payment Record
        payment = Payment.objects.create(
            user=request.user,
            subscription=subscription,
            amount=pkg_price,
            payment_method='EasyPaisa',
            easypaisa_number='03454524086',
            sender_number=sender_number or getattr(request.user.profile, 'phone_number', ''),
            transaction_id=transaction_id,
            payment_screenshot=screenshot,
            payment_date=timezone.now(),
            verification_status='pending'
        )

        # Create In-App Notification
        Notification.objects.create(
            user=request.user,
            title="🟡 Payment Under Verification",
            message=f"We have received your payment request for {pkg_name} (TRX: {transaction_id}). Our NOC team is verifying it and your package will be activated shortly.",
            link=f"/payments/receipt/{payment.id}/"
        )

        messages.info(request, "Your payment is under verification. Please wait. Your internet package will be activated shortly.")
        return redirect('view_receipt', payment_id=payment.id)

    context = {
        'packages': packages,
        'preselected_package': preselected_package,
        'preselected_custom_speed': preselected_custom_speed,
        'preselected_custom_price': preselected_custom_price,
        'initial_pkg': initial_pkg,
        'initial_is_custom': initial_is_custom,
        'initial_name': initial_name,
        'initial_speed': initial_speed,
        'initial_price': initial_price,
        'today_str': today_str,
        'default_expiry': default_expiry,
        'default_expiry_formatted': default_expiry_formatted,
    }
    return render(request, 'packages/select_package.html', context)


def api_calculate_expiry(request):
    date_str = request.GET.get('date')
    if not date_str:
        chosen_date = datetime.date.today()
    else:
        try:
            chosen_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            chosen_date = datetime.date.today()

    expiry = calculate_expiry_date(chosen_date)
    return JsonResponse({
        'status': 'success',
        'start_date': chosen_date.strftime('%Y-%m-%d'),
        'start_date_formatted': chosen_date.strftime('%B %d, %Y'),
        'expiry_date': expiry.strftime('%Y-%m-%d'),
        'expiry_date_formatted': expiry.strftime('%B %d, %Y'),
    })


def api_calculate_custom_price(request):
    try:
        speed = max(2, min(30, int(request.GET.get('speed', 10))))
    except (ValueError, TypeError):
        speed = 10
    price = calculate_custom_price(speed)
    return JsonResponse({
        'status': 'success',
        'speed': speed,
        'price': float(price),
        'price_formatted': f"Rs. {price:,.0f}"
    })
