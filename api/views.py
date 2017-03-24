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

from .models import Bidlet, Property, Bidding, Bidders
from .serializers import BidletSerializer, PropertySerializer, BiddingSerializer, BiddersSerializer

class BidletList(generics.ListCreateAPIView):
	"""
	API endpoint for listing and creating bid objects
	"""
	# queryset = Bidlet.objects.all()
	# serializer_class = BidletSerializer
	# print(queryset[0].id)
	# print(queryset[0].property)
	# print(queryset[0].owner)

class UserList(generics.ListCreateAPIView):

	queryset = Bidlet.objects.all()
	serializer_class = BidletSerializer

class Listings(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'listings.html'

    def get(self, request):
        listings = Property.objects.all()
        return Response({'listings': listings, 'CreatePropertyForm':CreatePropertyForm() , 'SearchPropertyForm': SearchPropertyForm})

# def searchListings(request):
# 	form = SearchPropertyForm(request.POST)
# 	if form.is_valid():
# 		bidPrice = form.cleaned_data['bidPrice']
# 	return HttpResponseRedirect('/api/property/'+ str(propertyID))

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
	print(form)
	if form.is_valid():
		bidPrice = form.cleaned_data['bidPrice']
		# TODO: MAKE UserID DYNAMIC
		userID = 69
		biddingID = bid.biddingID
		bid = Bidders.objects.create(userID=userID, bidPrice=bidPrice, biddingID=biddingID)
		Bidding.objects.filter(biddingID=biddingID).update(CurPrice=bid.bidPrice)
	return HttpResponseRedirect('/api/property/'+ str(propertyID))

def createProperty(request):
	form = CreatePropertyForm(request.POST)
	print(form)
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

	# TO DO: get userID
	ownerID = 1

	newProp = Property.objects.create(title= title, description=description, ownerID=ownerID, address=address, 
		country=country, city=city, postalCode=postalCode, suite=suite, image=image, startPrice=startPrice)
	bidding = Bidding.objects.create(biddingID=newProp.propertyID, propertyID=newProp.propertyID, startPrice=newProp.startPrice, 
		CurPrice=newProp.startPrice, ownerID=newProp.ownerID, dateStart=dateStart, dateEnd=dateEnd)
	return HttpResponseRedirect('/api/property/'+ str(newProp.propertyID))

class propertyDetails(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'property.html'

    def get(self, request, id):
        property = Property.objects.get(propertyID=id)
        bidding = Bidding.objects.get(propertyID=id)
        bidders = Bidders.objects.filter(biddingID=bidding.biddingID)
        form = BidForm(request.POST) #, bidPrice=bidding.CurPrice
        return Response({'property': property, 'bidding': bidding, 'bidders': bidders, 'form': form})