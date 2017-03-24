from django.contrib.auth import (
    get_user_model,
    authenticate,
    login,
    logout,
)

from datetime import date
from django import forms
from .models import Account

User = get_user_model()

class AccountLoginForm(forms.Form):
    username = forms.CharField()
    # Password input hides the password when typing (built in functionality for django)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("This user does not exist. Please confirm credentials")

            if not user.is_active:
                raise forms.ValidationError("User is not active")

            if not user.check_password(password):
                raise forms.ValidationError("Password is incorrect")

        return super(AccountLoginForm, self).clean(*args, **kwargs)

class UserRegistrationForm(forms.ModelForm):
    # Overwrite default email field, to make it required (not optional)
    email = forms.EmailField(label="Email Address")
    email2 = forms.EmailField(label="Confirm Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'email2',
            'password',
            'password2',
            'first_name',
            'last_name',
        ]

    def clean_email2(self):
        email = self.cleaned_data.get('email')
        email2 = self.cleaned_data.get('email2')
        if not email == email2:
            raise forms.ValidationError("Emails must match")

        email_queryset = User.objects.filter(email=email)
        if email_queryset.exists():
            raise forms.ValidationError("This email has already been registered")
        return email

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if not password == password2:
            raise forms.ValidationError("Passwords must match")

        return password

class AccountRegistrationForm(forms.ModelForm):
    birth_date = forms.DateField(label="Date of Birth")
    class Meta:
        model = Account
        fields = [
            'birth_date',
        ]

    # For liability reasons, check the age
    def clean_birth_date(self):
        birthday = self.cleaned_data.get('birth_date')
        today = date.today()

        if (today.year - birthday.year) < 16:
            # They are older than 16
            if ((today.month, today.day) < (birthday.month, birthday.day)):
                return birthday
            else:
                raise forms.ValidationError("You must be older than 16 to use this site")
        return birthday


class AccountEditForm(forms.ModelForm):

    LANGUAGE_CHOICES = (
        ('en','English'),
        ('fr', 'French'),
        ('ru','Russian'),
        ('es','Spanish'),
        ('it','Italian'),
    )
    CURRENCY_CHOICES = (
        ('cad','CAD ($)'),
        ('aud', 'AUD ($)'),
        ('usd','USD ($)'),
        ('gbp','GBP (£)'),
        ('eur','EUR (€)'),
        ('jpy','JPY (¥)'),
        ('hkd','HKD ($)'),
    )
    phone_regex = r'^\+?1?\d{8,20}$'
    phone_error_message = "Phone number must be numbers. Should be between 8 to 20 characters!"

    birth_date = forms.DateField(label="Date of Birth")
    phone_number = forms.RegexField(regex = phone_regex, error_message = phone_error_message, required=False)
    preferred_language = forms.ChoiceField(choices=LANGUAGE_CHOICES, required=False)
    preferred_currency = forms.ChoiceField(choices=CURRENCY_CHOICES, required=False)
    profile_description = forms.CharField(max_length=255, widget=forms.Textarea, required=False)

    class Meta:
        model = Account
        fields = [
            'birth_date',
            'phone_number',
            'preferred_language',
            'user_location',
            'profile_description',
            'preferred_currency',
            # 'profile_image'
        ]

    # For liability reasons, check the age
    def clean_birth_date(self):
        birthday = self.cleaned_data.get('birth_date')
        today = date.today()

        if (today.year - birthday.year) < 16:
            # They are older than 16
            if ((today.month, today.day) < (birthday.month, birthday.day)):
                return birthday
            else:
                raise forms.ValidationError("You must be older than 16 to use this site")
        return birthday
