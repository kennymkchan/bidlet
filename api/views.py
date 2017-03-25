import operator
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from django.http import HttpResponseRedirect
from django.db.models import Q
from functools import reduce
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import BidForm, CreatePropertyForm, SearchPropertyForm
from .models import Property, Bidding, Bidders
from users.models import Account
from .serializers import PropertySerializer, BiddingSerializer, BiddersSerializer

from django.conf import settings
import stripe


class Listings(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'listings.html'

    def get(self, request):
        listings = Property.objects.all()
        return Response({'listings': listings, 'CreatePropertyForm': CreatePropertyForm, 'SearchPropertyForm': SearchPropertyForm})

    def post(self, request):
        form = SearchPropertyForm(request.POST or None)
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
                    and_listings = Property.objects.filter(
                        reduce(operator.and_, andQuery))
                    listings = and_listings
                if orQuery:
                    or_listings = Property.objects.filter(
                        reduce(operator.or_, orQuery))
                    listings = or_listings
                if andQuery and orQuery and and_listings and or_listings:
                    listings = and_listings & or_listings
            search = {"AND": andPredicates, "OR": orPredicates}

        context = {
            'listings': listings,
            'CreatePropertyForm': CreatePropertyForm,
            'SearchPropertyForm': SearchPropertyForm,
            'search': search,
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

        biddingID = bid.biddingID

        try:
            autoWin = Property.objects.get(propertyID=biddingID).autoWinPrice
        except:
            autoWin = None

        bid = Bidders.objects.create(
            userID=userID, bidPrice=bidPrice, biddingID=biddingID)
        Bidding.objects.filter(biddingID=biddingID).update(
            curPrice=bid.bidPrice)
        Property.objects.filter(propertyID=biddingID).update(
            curPrice=bid.bidPrice)

    if autoWin is not None:
        # If user wishes to auto win the property
        if bidPrice >= autoWin:

            account_queryset = Account.objects.get(user_id=user.id)
            stripe.api_key = settings.STRIPE_KEY

            # The amount we charge for deposit will be equal to half the
            # bid price. * 100 because we need this value in cents
            # Autowin amount instead of bidPrice to protect user
            # Stripe does not take decimals!
            value = int(autoWin * 100 / 2)

            try:
                # Charging the customer
                stripe.Charge.create(
                    amount=value,
                    currency="cad",
                    customer=account_queryset.stripe_id,
                )
                messages.success(
                    request, 'Congratulations! You have won the auction!')
                return redirect('/property/' + str(propertyID))
            except:
                messages.error(
                    request, "Something went wrong, unable to charge credit card")
                return redirect('/property/' + str(propertyID))

            messages.success(
                request, 'You are now the highest bidder @ $' + str(bid.bidPrice))
            return HttpResponseRedirect('/property/' + str(propertyID))
    else:
        context['form'] = form
        context['property'] = Property.objects.get(propertyID=propertyID)
        return render(request, 'property.html', context)


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
        autoWinPrice = form.cleaned_data['autoWinPrice']
        dateStart = form.cleaned_data['dateStart']
        dateEnd = form.cleaned_data['dateEnd']
        availStart = form.cleaned_data['availStart']
        availEnd = form.cleaned_data['availEnd']
        rooms = form.cleaned_data['rooms']

        newProp = Property.objects.create(title=title, description=description,
                                          ownerID=ownerID, address=address, country=country, city=city,
                                          postalCode=postalCode, suite=suite, image=image,
                                          startPrice=startPrice, autoWinPrice=autoWinPrice,
                                          curPrice=startPrice, availStart=availStart, availEnd=availEnd,
                                          rooms=rooms)

        bidding = Bidding.objects.create(biddingID=newProp.propertyID,
                                         propertyID=newProp.propertyID, startPrice=newProp.startPrice,
                                         curPrice=newProp.startPrice, ownerID=newProp.ownerID,
                                         dateStart=dateStart, dateEnd=dateEnd)

        messages.success(request, 'Your new listing added!')
        return HttpResponseRedirect('/property/' + str(newProp.propertyID))


class propertyDetails(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'property.html'

    def get(self, request, id):
        property = Property.objects.get(propertyID=id)
        bidding = Bidding.objects.get(propertyID=id)
        bidders = Bidders.objects.filter(biddingID=bidding.biddingID)
        # , bidPrice=bidding.CurPrice
        form = BidForm(request.POST or None, propID=id)
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
