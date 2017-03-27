from django import forms
from datetime import datetime, timedelta
from .models import Bidding

class BidForm(forms.Form):
	bidPrice = forms.DecimalField(label="Your Bid Price", max_digits=8, decimal_places=2)

	def __init__(self, *args, **kwargs):
		# Passing in the property ID from the form so that we
		# can ensure we know the current price of the unit
		self.propertyID = kwargs.pop("propID")
		super(BidForm, self).__init__(*args, **kwargs)

	def clean_bidPrice(self):
		bid = self.cleaned_data.get("bidPrice")
		currentPriceQS = Bidding.objects.filter(propertyID=self.propertyID).first()

		if bid < currentPriceQS.curPrice + 10:
			raise forms.ValidationError("Bid must be greater than current bid price by at least $10.00")
		return bid

class CreatePropertyForm(forms.Form):
	title = forms.CharField(initial="4 Room suite sublet for FALL 2017")
	description = forms.CharField(initial="Best place ever")
	address = forms.CharField(initial="200 University ave")
	country = forms.CharField(initial="Canada")
	city = forms.CharField(initial="Waterloo", required=False)
	postalCode = forms.CharField(initial="L3R6Y7")
	suite = forms.IntegerField(initial=400, required=False)
	image = forms.CharField(initial="http://www.hawkswap.com/wp-content/uploads/2012/08/438421.jpg", required=False)
	startPrice = forms.DecimalField(initial=600)
	autoWinPrice = forms.DecimalField(initial=800, required=False)
	dateStart = forms.DateTimeField(initial=datetime.now())
	dateEnd = forms.DateTimeField(initial=datetime.now()+timedelta(days=10))
	availStart = forms.DateTimeField(initial=datetime.now()+timedelta(weeks=4))
	availEnd = forms.DateTimeField(initial=datetime.now()+timedelta(weeks=20), required=False)
	rooms = forms.IntegerField(initial=1)

	def clean_autoWinPrice(self):
		auto_win = self.cleaned_data.get("autoWinPrice")
		if auto_win <= self.cleaned_data.get("startPrice"):
			raise forms.ValidationError("Auto win cannot be less than start price")
		return auto_win

	def clean_dateEnd(self):
		dateStart = self.cleaned_data.get("dateStart")
		dateEnd = self.cleaned_data.get("dateEnd")
		if dateEnd < dateStart:
			raise forms.ValidationError("Please select an auction end date after the start date")
		return dateEnd

	def clean_availEnd(self):
		availStart = self.cleaned_data.get("availStart")
		availEnd = self.cleaned_data.get("availEnd")
		if availEnd < availStart:
			raise forms.ValidationError("Please select an contract end date after the start date")
		return availEnd

class EditPropertyForm(forms.Form):
	title = forms.CharField(required=False)
	description = forms.CharField(required=False)
	address = forms.CharField(required=False)
	country = forms.CharField(required=False)
	city = forms.CharField(required=False)
	postalCode = forms.CharField(required=False)
	# image = forms.CharField(required=False)

class SearchPropertyForm(forms.Form):
	keyword = forms.CharField(required=False)
	country = forms.CharField(required=False)
	city = forms.CharField(required=False)
	rooms = forms.IntegerField(required=False)
	availStart = forms.DateTimeField(label="Move-in Date", required=False)
	availEnd = forms.DateTimeField(label="Move-out Date", required=False)
	priceUnder = forms.IntegerField(label="Price under", required=False)
	priceOver = forms.IntegerField(label="Price over", required=False)
