from rest_framework import generics
from rest_framework.response import Response
from django.views.generic import TemplateView
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.views import APIView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.db.models import Q
import operator
from functools import reduce

from .forms import BidForm, CreatePropertyForm, SearchPropertyForm

from .models import Property, Bidding, Bidders
from .serializers import PropertySerializer, BiddingSerializer, BiddersSerializer

from django.shortcuts import render

from django.contrib.auth.decorators import login_required

class Listings(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'listings.html'

    def get(self, request):
        listings = Property.objects.all()
        return Response({'listings': listings, 'CreatePropertyForm':CreatePropertyForm() , 'SearchPropertyForm': SearchPropertyForm})

class searchListings(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'listings.html'

    def post(self, request):
    	form = SearchPropertyForm(request.POST)
    	print(form)
    	if form.is_valid():
    		predicates = []
    		country = form.cleaned_data['country']
    		city = form.cleaned_data['city']
    		keyword = form.cleaned_data['keyword']
    		if country:
    			predicates.append(('country__contains', country))
    		if city:
    			predicates.append(('city__contains', city))
    		if keyword:
    			predicates.append(('title__contains', keyword))
    			# TO DO: SEARCH FOR DESCRIPTION USING OR
    		q_list = [Q(x) for x in predicates]
    		listings = Property.objects.filter(reduce(operator.and_, q_list))
    		search = predicates
    	return Response({'listings': listings, 'CreatePropertyForm':CreatePropertyForm() , 'SearchPropertyForm': SearchPropertyForm, 'search':search})

def createBid(request, propertyID=None):
	bid = Bidding.objects.get(propertyID=propertyID)
	form = BidForm(request.POST)
	if form.is_valid():
		bidPrice = form.cleaned_data['bidPrice']
		# TODO: MAKE UserID DYNAMIC

		user = request.user
		print(user.id)
		if user.is_authenticated:
			userID = user.id

		biddingID = bid.biddingID

		bid = Bidders.objects.create(userID=userID, bidPrice=bidPrice, biddingID=biddingID)
		Bidding.objects.filter(biddingID=biddingID).update(CurPrice=bid.bidPrice)
	return HttpResponseRedirect('/property/'+ str(propertyID))

def createProperty(request):
	form = CreatePropertyForm(request.POST or None)

	user = request.user
	if user.is_authenticated:
		ownerID = user.id

	title = form.cleaned_data['title']
	description = form.cleaned_data['description']
	address = form.cleaned_data['address']
	country = form.cleaned_data['country']
	city = form.cleaned_data['city']
	postalCode = form.cleaned_data['postalCode']
	suite = form.cleaned_data['suite']
	image = form.cleaned_data['image']
	startPrice = form.cleaned_data['startPrice']
	dateStart = form.cleaned_data['dateStart']
	dateEnd = form.cleaned_data['dateEnd']

	newProp = Property.objects.create(title= title, description=description, ownerID=ownerID, address=address,
		country=country, city=city, postalCode=postalCode, suite=suite, image=image, startPrice=startPrice)
	bidding = Bidding.objects.create(biddingID=newProp.propertyID, propertyID=newProp.propertyID, startPrice=newProp.startPrice,
		CurPrice=newProp.startPrice, ownerID=newProp.ownerID, dateStart=dateStart, dateEnd=dateEnd)
	return HttpResponseRedirect('/property/'+ str(newProp.propertyID))

class propertyDetails(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'property.html'

    def get(self, request, id):
        property = Property.objects.get(propertyID=id)
        bidding = Bidding.objects.get(propertyID=id)
        bidders = Bidders.objects.filter(biddingID=bidding.biddingID)
        form = BidForm(request.POST) #, bidPrice=bidding.CurPrice
        return Response({'property': property, 'bidding': bidding, 'bidders': bidders, 'form': form})
