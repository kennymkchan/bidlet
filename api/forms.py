from django import forms
from datetime import *
# from .models import Bidding

class BidForm(forms.Form):
	bidPrice = forms.DecimalField(label="Your Bid Price", max_digits=8, decimal_places=2)

class CreatePropertyForm(forms.Form):
	# TODO: Remove the initial
	title = forms.CharField(initial="4 Room suite sublet for FALL 2017")
	description = forms.CharField(initial="Best place ever")
	address = forms.CharField(initial="200 University ave")
	country = forms.CharField(initial="Canada")
	city = forms.CharField(initial="Waterloo")
	postalCode = forms.CharField(initial="L3R6Y7")
	suite = forms.IntegerField(initial=400)
	image = forms.CharField(initial="http://www.hawkswap.com/wp-content/uploads/2012/08/438421.jpg")
	startPrice = forms.DecimalField(initial=600)

	dateStart = forms.DateTimeField(initial=datetime.now())
	dateEnd = forms.DateTimeField(initial=datetime.now())

class SearchPropertyForm(forms.Form):
	keyword = forms.CharField(required=False)
	country = forms.CharField(required=False)
	city = forms.CharField(required=False)
