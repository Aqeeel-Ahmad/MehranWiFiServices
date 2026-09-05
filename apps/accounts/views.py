from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import UserProfile
from .forms import UserProfileUpdateForm
from apps.packages.models import PackageSubscription
from apps.payments.models import Payment
from apps.complaints.models import Complaint
from apps.notifications.models import Notification

def register_view(request):
    return redirect('account_signup')


def login_view(request):
    next_url = request.GET.get('next')
    if next_url:
        return redirect(f'/accounts/login/?next={next_url}')
    return redirect('account_login')


def logout_view(request):
    return redirect('account_logout')


@login_required
def dashboard_view(request):
    user = request.user
    
    # Active Subscription (verified & within expiry)
    active_sub = PackageSubscription.objects.filter(
        user=user,
        status='active'
    ).order_by('-activation_date').first()

    # Pending Subscription (under verification)
    pending_sub = PackageSubscription.objects.filter(
        user=user,
        status='pending'
    ).order_by('-created_at').first()

    # Summary statistics
    all_subs = PackageSubscription.objects.filter(user=user)
    total_packages_count = all_subs.count()
    all_payments = Payment.objects.filter(user=user).select_related('subscription')
    total_spent = sum(p.amount for p in all_payments.filter(verification_status='verified'))

    # Recent payments
    recent_payments = all_payments[:5]

    # Recent complaints
    recent_complaints = Complaint.objects.filter(user=user)[:3]

    # Notifications
    notifications = Notification.objects.filter(user=user)[:5]

    context = {
        'user': user,
        'profile': getattr(user, 'profile', None),
        'active_sub': active_sub,
        'pending_sub': pending_sub,
        'total_packages_count': total_packages_count,
        'total_spent': total_spent,
        'recent_payments': recent_payments,
        'recent_complaints': recent_complaints,
        'notifications': notifications,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile_view(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            user.first_name = form.cleaned_data.get('first_name', '')
            user.last_name = form.cleaned_data.get('last_name', '')
            user.email = form.cleaned_data.get('email', '')
            user.save()
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('profile')
    else:
        initial_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
        form = UserProfileUpdateForm(instance=profile, initial=initial_data)

    return render(request, 'accounts/profile.html', {'form': form, 'user': user, 'profile': profile})
