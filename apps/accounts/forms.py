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
