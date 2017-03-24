from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

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

# Only need if I am planning to do triggers

# @receiver(post_save, sender=User)
# def create_user_account(sender, instance, created, **kwargs):
#     if created:
#         Account.objects.create(user=instance)
#
# @receiver(post_save, sender=User)
# def save_user_account(sender, instance, **kwargs):
#     instance.account.save()
