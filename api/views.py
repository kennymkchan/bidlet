from rest_framework import generics
from rest_framework.response import Response
from django.views.generic import TemplateView
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.views import APIView
from django.http import HttpResponseRedirect
from django.db.models import Q
import operator
from functools import reduce
from django.shortcuts import render
from django.contrib import messages

from .forms import BidForm, CreatePropertyForm, SearchPropertyForm

from .models import Property, Bidding, Bidders
from users.models import Account
from .serializers import PropertySerializer, BiddingSerializer, BiddersSerializer

from django.contrib.auth.decorators import login_required

class Listings(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'listings.html'

    def get(self, request):
        listings = Property.objects.all()
        return Response({'listings': listings, 'CreatePropertyForm':CreatePropertyForm , 'SearchPropertyForm': SearchPropertyForm})

    def post(self, request):
    	form = SearchPropertyForm(request.POST or None)
    	print(form)
    	if form.is_valid():
    		andPredicates = []
    		orPredicates = []
    		country = form.cleaned_data['country']
    		city = form.cleaned_data['city']
    		keyword = form.cleaned_data['keyword']
    		rooms = form.cleaned_data['rooms']
    		availStart = form.cleaned_data['availStart']
    		availEnd = form.cleaned_data['availEnd']
    		priceUnder = form.cleaned_data['priceUnder']
    		priceOver = form.cleaned_data['priceOver']

    		if country:
    			andPredicates.append(('country__icontains', country))
    		if city:
    			andPredicates.append(('city__icontains', city))
    		if keyword:
    			orPredicates.append(('title__icontains', keyword))
    			orPredicates.append(('description__icontains', keyword))
    		if rooms:
    			andPredicates.append(('rooms__exact', rooms))
    		if availStart:
    			andPredicates.append(('availStart__lte', availStart))
    		if availEnd:
    			andPredicates.append(('availEnd__gte', availEnd))
    		if priceUnder:
    			andPredicates.append(('curPrice__lte', priceUnder))
    		if priceOver:
    			andPredicates.append(('curPrice__gte', priceOver))

    		andQuery = [Q(x) for x in andPredicates]
    		orQuery = [Q(x) for x in orPredicates]

    		if not andQuery and not orQuery:
    			listings = Property.objects.all()
    		else:
	    		if andQuery:
	    			and_listings = Property.objects.filter(reduce(operator.and_, andQuery))
	    			listings = and_listings
	    		if orQuery:
	    			or_listings = Property.objects.filter(reduce(operator.or_, orQuery))
	    			listings = or_listings
	    		if andQuery and orQuery and and_listings and or_listings:
	    			listings = and_listings & or_listings
    		search = { "AND": andPredicates, "OR": orPredicates}

    	context = {
			'listings': listings,
			'CreatePropertyForm':CreatePropertyForm,
			'SearchPropertyForm': SearchPropertyForm,
			'search':search
		}

    	return Response(context)

def createBid(request, propertyID=None):
	context = {}
	bid = Bidding.objects.get(propertyID=propertyID)
	form = BidForm(request.POST or None, propID=bid.propertyID)
	if form.is_valid():
		bidPrice = form.cleaned_data['bidPrice']

		# see if the user is authenticated. If they are, take their ID
		user = request.user
		if user.is_authenticated:
			userID = user.id
		# fail safe
		else:
			userID = 1

		# Allow for Now
		# TODO: DO NOT LET OWNER BID ON THEIR OWN PROPERTY
		# prop = Property.objects.get(propertyID=propertyID)
		# if userID == prop.ownerID:
		# 	messages.error(request, 'You cannot bid on your own property')
		# 	return HttpResponseRedirect('/property/'+ str(propertyID))		


		biddingID = bid.biddingID

		bid = Bidders.objects.create(userID=userID, bidPrice=bidPrice, biddingID=biddingID)
		Bidding.objects.filter(biddingID=biddingID).update(curPrice=bid.bidPrice)
		Property.objects.filter(propertyID=biddingID).update(curPrice=bid.bidPrice)

		messages.success(request, 'You are now the highest bidder @ $' + str(bid.bidPrice))
		return HttpResponseRedirect('/property/'+ str(propertyID))
	else:
		context['form'] = form
		context['property'] = Property.objects.get(propertyID=propertyID)
		return render(request,'property.html', context)

def createProperty(request):
	form = CreatePropertyForm(request.POST or None)

	# see if the user is authenticated. If they are, take their ID
	user = request.user
	if user.is_authenticated:
		ownerID = user.id
	else:
		# fail safe
		ownerID = 1

	if form.is_valid():
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
		availStart = form.cleaned_data['availStart']
		availEnd = form.cleaned_data['availEnd']
		rooms = form.cleaned_data['rooms']

		newProp = Property.objects.create(title= title, description=description, ownerID=ownerID, address=address,
			country=country, city=city, postalCode=postalCode, suite=suite, image=image, startPrice=startPrice, curPrice=startPrice, availStart=availStart, availEnd=availEnd, rooms=rooms)
		bidding = Bidding.objects.create(biddingID=newProp.propertyID, propertyID=newProp.propertyID, startPrice=newProp.startPrice,
			curPrice=newProp.startPrice, ownerID=newProp.ownerID, dateStart=dateStart, dateEnd=dateEnd)

		messages.success(request, 'Your new listing added!')
		return HttpResponseRedirect('/property/'+ str(newProp.propertyID))

class propertyDetails(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'property.html'

    def get(self, request, id):
        property = Property.objects.get(propertyID=id)
        bidding = Bidding.objects.get(propertyID=id)
        bidders = Bidders.objects.filter(biddingID=bidding.biddingID)
        form = BidForm(request.POST or None, propID=id) #, bidPrice=bidding.CurPrice
        currentUser = bidders.last()
        if request.user.is_authenticated():
            account = Account.objects.get(user_id=request.user.id).stripe_id
        else:
            account = None
        context = {
            'property': property,
            'bidding': bidding,
            'bidders': bidders,
            'form': form,
            'currentUser': currentUser,
            'account': account
        }
        return Response(context)
