from django import forms
from django.contrib.auth.models import User
from allauth.account.forms import SignupForm, LoginForm
from .models import UserProfile
from apps.notifications.models import Notification

class CustomAllauthLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'login' in self.fields:
            self.fields['login'].widget.attrs.update({
                'class': 'form-control',
                'placeholder': 'Enter username or email',
                'autofocus': 'autofocus'
            })
        if 'password' in self.fields:
            self.fields['password'].widget.attrs.update({
                'class': 'form-control',
                'placeholder': 'Enter your password'
            })

class CustomAllauthSignupForm(SignupForm):
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 03001234567'})
    )
    whatsapp_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 03001234567 (Optional)'})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'House / Street, Area, City'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-control')
        if 'email' in self.fields:
            self.fields['email'].widget.attrs.update({'placeholder': 'name@example.com', 'class': 'form-control'})
        if 'username' in self.fields:
            self.fields['username'].widget.attrs.update({'placeholder': 'Choose username', 'class': 'form-control'})
        if 'password1' in self.fields:
            self.fields['password1'].widget.attrs.update({'placeholder': 'Enter strong password', 'class': 'form-control'})
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm password', 'class': 'form-control'})

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save(update_fields=['first_name', 'last_name'])

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.phone_number = self.cleaned_data.get('phone_number', '')
        profile.whatsapp_number = self.cleaned_data.get('whatsapp_number', '') or profile.phone_number
        profile.address = self.cleaned_data.get('address', '')
        profile.save()

        Notification.objects.create(
            user=user,
            title="👋 Welcome to Mehran WiFi Service!",
            message="Your account has been created. Explore our fiber internet packages to get connected.",
            link="/packages/"
        )
        return user


class UserRegisterForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}))
    phone_number = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 03001234567'}))
    whatsapp_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 03001234567 (Optional)'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'House / Street, Area, City'}), required=False)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter strong password'}), min_length=6)
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Re-enter password'}), min_length=6)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose username'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password_confirm')
        if p1 and p2 and p1 != p2:
            self.add_error('password_confirm', "Passwords do not match.")
        return cleaned_data


class UserLoginForm(forms.Form):
    username_or_email = forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username or email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'})
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'rememberMe'})
    )


class UserProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    whatsapp_number = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False)

    class Meta:
        model = UserProfile
        fields = ['phone_number', 'whatsapp_number', 'address', 'profile_image']
