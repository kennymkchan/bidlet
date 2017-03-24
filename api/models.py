from django.db import models

class Bidlet(models.Model):
	id = models.AutoField(primary_key=True)
	property = models.CharField(max_length=200, unique=True)
	owner = models.CharField(max_length=100)
  
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
	biddingID = models.IntegerField(blank=True, null=True)
	availStart = models.DateTimeField()
	availEnd = models.DateTimeField()
	rooms = models.IntegerField()

class Bidding(models.Model):
	biddingID = models.AutoField(primary_key=True)
	propertyID = models.IntegerField()
	startPrice = models.DecimalField(max_digits=8, decimal_places=2)
	CurPrice = models.DecimalField(max_digits=8, decimal_places=2)
	ownerID = models.IntegerField()
	dateStart = models.DateTimeField()
	dateEnd = models.DateTimeField()

class Bidders(models.Model):
	biddingID = models.IntegerField()
	userID = models.IntegerField()
	bidPrice = models.DecimalField(max_digits=8, decimal_places=2)

