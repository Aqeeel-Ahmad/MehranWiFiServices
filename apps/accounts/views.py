from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import UserRegisterForm, UserLoginForm, UserProfileUpdateForm
from apps.packages.models import PackageSubscription
from apps.payments.models import Payment
from apps.complaints.models import Complaint
from apps.notifications.models import Notification

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Save profile details
            profile = user.profile
            profile.phone_number = form.cleaned_data.get('phone_number', '')
            profile.whatsapp_number = form.cleaned_data.get('whatsapp_number', '') or profile.phone_number
            profile.address = form.cleaned_data.get('address', '')
            profile.save()

            # Welcome notification
            Notification.objects.create(
                user=user,
                title="👋 Welcome to Mehran WiFi Service!",
                message="Your account has been created. Explore our fiber internet packages to get connected.",
                link="/packages/"
            )

            # Auto-login after registration
            login(request, user)
            messages.success(request, f"Welcome to Mehran WiFi Service, {user.username}! Your account has been created.")
            return redirect('dashboard')
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    next_url = request.GET.get('next', 'dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data.get('username_or_email')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')

            # Find user by username or email
            user_obj = None
            if '@' in username_or_email:
                user_obj = User.objects.filter(email__iexact=username_or_email).first()
                username = user_obj.username if user_obj else None
            else:
                username = username_or_email

            user = authenticate(request, username=username, password=password)
            if user is not None:
                if not user.is_active:
                    messages.error(request, "This account is inactive. Please contact Mehran WiFi support.")
                    return render(request, 'accounts/login.html', {'form': form})

                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)  # Expires when browser closes
                else:
                    request.session.set_expiry(1209600)  # 2 weeks

                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                return redirect(next_url if next_url and next_url != '/' else 'dashboard')
            else:
                messages.error(request, "Invalid username/email or password. Please try again.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')


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
