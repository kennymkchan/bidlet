from django.db import models
from django.contrib.auth.models import User

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    preferred_language = models.CharField(max_length=10, blank=True, null=True)
    user_location = models.CharField(max_length=65, blank=True, null=True)
    profile_description = models.CharField(max_length=255, blank=True, null=True)
    preferred_currency = models.CharField(max_length=4, blank=True, null=True)
    profile_image = models.FileField(blank=True, null=True)
    stripe_id = models.CharField(max_length=30, blank=True, null=True)
