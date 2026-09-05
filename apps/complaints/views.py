from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Complaint
from apps.notifications.models import Notification

def submit_complaint_view(request):
    if request.method == 'POST':
        user_name = request.POST.get('user_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        subject = request.POST.get('subject', '').strip()
        description = request.POST.get('description', '').strip()

        if not user_name or not phone_number or not subject or not description:
            messages.error(request, "Please fill out all fields in the complaint form.")
            return redirect(request.META.get('HTTP_REFERER', 'home'))

        complaint = Complaint.objects.create(
            user=request.user if request.user.is_authenticated else None,
            user_name=user_name,
            phone_number=phone_number,
            subject=subject,
            description=description,
            status='pending'
        )

        if request.user.is_authenticated:
            Notification.objects.create(
                user=request.user,
                title="🛠️ Complaint Registered",
                message=f"Ticket #{complaint.ticket_number} has been logged. Our fiber technician is reviewing your issue.",
                link="/complaints/"
            )

        messages.success(request, f"Your complaint has been submitted successfully! Your Ticket ID is #{complaint.ticket_number}. A technician will contact you shortly.")
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    return render(request, 'complaints/complaint_form.html')


@login_required
def complaint_list_view(request):
    complaints = Complaint.objects.filter(user=request.user)
    return render(request, 'complaints/complaint_list.html', {'complaints': complaints})
