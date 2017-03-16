from django.db import models

class Bidlet(models.Model):
	property = models.CharField(max_length=200, unique=True)
	owner = models.CharField(max_length=100)
