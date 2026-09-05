from django.shortcuts import render, redirect
from django.contrib import messages
from apps.packages.models import InternetPackage, PackageSubscription
from apps.core.models import SpecialOffer, Feedback, ContactMessage

def home_view(request):
    packages = InternetPackage.objects.filter(is_active=True).exclude(speed_mbps__in=[15, 30], is_custom=False).order_by('display_order', 'speed_mbps')
    special_offers = SpecialOffer.objects.filter(is_active=True)
    feedbacks = Feedback.objects.filter(is_approved=True).order_by('-created_at')[:6]

    active_subscription = None
    if request.user.is_authenticated:
        active_subscription = PackageSubscription.objects.filter(
            user=request.user,
            status='active'
        ).first()

    context = {
        'packages': packages,
        'special_offers': special_offers,
        'feedbacks': feedbacks,
        'active_subscription': active_subscription,
    }
    return render(request, 'core/index.html', context)


def about_view(request):
    return render(request, 'core/about.html')


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if not name or not email or not message:
            messages.error(request, "Please provide your name, email, and message.")
            return redirect('contact')

        ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            subject=subject or 'General Inquiry',
            message=message
        )
        messages.success(request, "Thank you for reaching out! Our HAM 3 NETWORK team has received your message and will get back to you shortly.")
        return redirect('contact')

    return render(request, 'core/contact.html')


def submit_feedback_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        try:
            rating = int(request.POST.get('rating', 5))
        except (ValueError, TypeError):
            rating = 5
        message = request.POST.get('message', '').strip()

        if not name or not email or not message:
            messages.error(request, "Please complete all feedback fields.")
            return redirect(request.META.get('HTTP_REFERER', 'home'))

        Feedback.objects.create(
            user=request.user if request.user.is_authenticated else None,
            name=name,
            email=email,
            rating=rating,
            message=message,
            is_approved=True
        )
        messages.success(request, "Thank you for your valuable feedback! We appreciate your trust in HAM 3 NETWORK.")
        return redirect(request.META.get('HTTP_REFERER', 'home') + '#feedback-section')

    return redirect('home')
