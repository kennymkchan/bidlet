from django.db import models

class Property(models.Model):
	propertyID = models.AutoField(primary_key=True)
	title = models.CharField(max_length=200)
	description = models.CharField(max_length=250)
	ownerID = models.IntegerField()
	address = models.CharField(max_length=200)
	country = models.CharField(max_length=100)
	city = models.CharField(max_length=100)
	postalCode = models.CharField(max_length=6)
	suite = models.IntegerField(blank=True, null=True)
	image = models.CharField(max_length=200)
	startPrice = models.DecimalField(max_digits=8, decimal_places=2)
	autoWinPrice = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
	curPrice = models.DecimalField(max_digits=8, decimal_places=2,blank=True, null=True)
	biddingID = models.IntegerField(blank=True, null=True)
	availStart = models.DateTimeField(blank=True, null=True)
	availEnd = models.DateTimeField(blank=True, null=True)
	rooms = models.IntegerField(blank=True, null=True)

class Bidding(models.Model):
	biddingID = models.AutoField(primary_key=True)
	propertyID = models.IntegerField()
	startPrice = models.DecimalField(max_digits=8, decimal_places=2)
	curPrice = models.DecimalField(max_digits=8, decimal_places=2)
	ownerID = models.IntegerField()
	dateStart = models.DateTimeField()
	dateEnd = models.DateTimeField()

class Bidders(models.Model):
	biddingID = models.IntegerField()
	userID = models.IntegerField()
	bidPrice = models.DecimalField(max_digits=8, decimal_places=2)
