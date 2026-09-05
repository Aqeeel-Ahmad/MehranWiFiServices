import json
from allauth.account.adapter import DefaultAccountAdapter
from apps.accounts.models import UserProfile
from apps.notifications.models import Notification

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        # Call the parent class to populate default fields (username, email)
        user = super().save_user(request, user, form, commit=False)

        # Extract extra fields depending on whether the request is JSON (headless API) or standard POST
        first_name = ''
        last_name = ''
        phone_number = ''
        whatsapp_number = ''
        address = ''

        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                first_name = data.get('first_name', '')
                last_name = data.get('last_name', '')
                phone_number = data.get('phone_number', '')
                whatsapp_number = data.get('whatsapp_number', '')
                address = data.get('address', '')
            except (json.JSONDecodeError, AttributeError):
                pass
        else:
            first_name = form.cleaned_data.get('first_name', '')
            last_name = form.cleaned_data.get('last_name', '')
            phone_number = form.cleaned_data.get('phone_number', '')
            whatsapp_number = form.cleaned_data.get('whatsapp_number', '')
            address = form.cleaned_data.get('address', '')

        # Set user attributes
        user.first_name = first_name
        user.last_name = last_name
        
        if commit:
            user.save()
            
            # Create or update UserProfile
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.phone_number = phone_number
            profile.whatsapp_number = whatsapp_number or phone_number
            profile.address = address
            profile.save()

            # Ensure the EmailAddress is verified (similar to the CustomAllauthSignupForm logic)
            from allauth.account.models import EmailAddress
            EmailAddress.objects.filter(user=user, email__iexact=user.email).update(verified=True, primary=True)
            
            # Send notification
            Notification.objects.create(
                user=user,
                title="👋 Welcome to Mehran WiFi Service!",
                message="Your account has been created. Explore our fiber internet packages to get connected.",
                link="/packages/"
            )
            
        return user
