from django.db import models

class Bidlet(models.Model):
	id = models.AutoField(primary_key=True)
	property = models.CharField(max_length=200, unique=True)
	owner = models.CharField(max_length=100)
	cost = models.IntegerField
