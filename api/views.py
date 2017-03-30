import operator
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from django.http import HttpResponseRedirect
from django.db.models import Q
from functools import reduce
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import BidForm, CreatePropertyForm, SearchPropertyForm, EditPropertyForm
from .models import Property, Bidding, Bidders
from users.models import Account
from django.contrib.auth.decorators import login_required
from .serializers import PropertySerializer, BiddingSerializer, BiddersSerializer
from datetime import datetime, timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import stripe


class Listings(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'listings.html'

    def get(self, request):
        listings = Property.objects.all().exclude(status="inactive")
        context = {
            'listings': listings,
            'CreatePropertyForm': CreatePropertyForm,
            'SearchPropertyForm': SearchPropertyForm
        }
        return Response(context)

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
                listings = Property.objects.all().exclude(status="inactive")
            else:
                if andQuery:
                    and_listings = Property.objects.filter(
                        reduce(operator.and_, andQuery)).exclude(status="inactive")
                    listings = and_listings
                if orQuery:
                    or_listings = Property.objects.filter(
                        reduce(operator.or_, orQuery)).exclude(status="inactive")
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


@login_required(login_url="/login/")
def createBid(request, propertyID=None):
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

        sublet = Property.objects.get(propertyID=biddingID)

        # Make sure that the bid is still placeable, and auction has not ended
        # Accounts for the edge case the user has the page open but auction
        # ends
        try:
            if datetime.now(timezone.utc) > bid.dateEnd:
                messages.error(
                    request, 'Error 800: Auction is over, unable to place bid')
                return HttpResponseRedirect('/property/' + str(propertyID))
        except:
            pass

        try:
            autoWin = sublet.autoWinPrice
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
                return chargeCustomer(request, user.id, autoWin, propertyID)

        messages.success(
            request, 'You are now the highest bidder @ $' + str(bid.bidPrice))
        return HttpResponseRedirect('/property/' + str(propertyID))
    else:
        messages.error(
            request, 'Please increase your bid to over $' + str(bid.curPrice + 10))
        return HttpResponseRedirect('/property/' + str(propertyID))


@login_required(login_url="/login/")
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
                                          rooms=rooms, status="active")

        bidding = Bidding.objects.create(biddingID=newProp.propertyID,
                                         propertyID=newProp.propertyID, startPrice=newProp.startPrice,
                                         curPrice=newProp.startPrice, ownerID=newProp.ownerID,
                                         dateStart=dateStart, dateEnd=dateEnd)

        messages.success(request, 'Your new listing added!')
        return HttpResponseRedirect('/property/' + str(newProp.propertyID))

    context = {
        "CreatePropertyForm": form,
    }

    return render(request, 'property/create_property.html', context)


@login_required(login_url="/login/")
def property_edit_view(request, propertyID=None):
    user = request.user

    property_queryset = Property.objects.get(propertyID=propertyID)

    # Make sure the user is the owner
    if user.id != property_queryset.ownerID:
        messages.success(
            request, 'Access Restricted! Cannot access this property')
        return HttpResponseRedirect('/property/' + str(property_queryset.propertyID))

    # Without None, it will always be initialized with a post (tries to post
    # to db)
    propertyEditForm = EditPropertyForm(
        request.POST or None, request.FILES or None)

    propertyEditForm.fields["title"].initial = property_queryset.title
    propertyEditForm.fields["description"].initial = property_queryset.description
    propertyEditForm.fields["address"].initial = property_queryset.address
    propertyEditForm.fields["country"].initial = property_queryset.country
    propertyEditForm.fields["city"].initial = property_queryset.city
    propertyEditForm.fields["postalCode"].initial = property_queryset.postalCode
    # TODO: Consider adding image change capabilities

    if propertyEditForm.is_valid():

        title = propertyEditForm.cleaned_data['title']
        description = propertyEditForm.cleaned_data['description']
        address = propertyEditForm.cleaned_data['address']
        country = propertyEditForm.cleaned_data['country']
        city = propertyEditForm.cleaned_data['city']
        postalCode = propertyEditForm.cleaned_data['postalCode']

        try:
            Property.objects.filter(propertyID=propertyID).update(
                title=title, description=description,
                address=address, country=country,
                city=city, postalCode=postalCode,
            )

            messages.success(request, 'Information updated successfully!')
            return HttpResponseRedirect('/property/' + str(property_queryset.propertyID))

        except:
            messages.eroor(
                request, 'An error has occured. Please contact system admins!')
            return HttpResponseRedirect('/property/' + str(property_queryset.propertyID))

    context = {
        "propertyEditForm": propertyEditForm,
        "sublet": property_queryset,
    }
    return render(request, 'property/edit_property.html', context)


class propertyDetails(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'property.html'

    def get(self, request, id):
        property = Property.objects.get(propertyID=id)
        bidding = Bidding.objects.get(propertyID=id)
        bidders = Bidders.objects.filter(biddingID=bidding.biddingID)

        form = BidForm(request.POST or None, propID=id)
        currentUser = bidders.last()
        if request.user.is_authenticated():
            account = Account.objects.get(user_id=request.user.id).stripe_id
        else:
            account = None

        if datetime.now(timezone.utc) > bidding.dateEnd:
            can_bid = False
        else:
            can_bid = True
        context = {
            'property': property,
            'bidding': bidding,
            'bidders': bidders,
            'form': form,
            'currentUser': currentUser,
            'payment': account,
            'can_bid': can_bid,
        }
        return Response(context)


def chargeCustomer(request, userID, autoWin, propertyID):
    account_queryset = Account.objects.get(user_id=userID)
    stripe.api_key = settings.STRIPE_KEY
    user = request.user

    # The amount we charge for deposit will be equal to half the
    # bid price. * 100 because we need this value in cents
    # Autowin amount instead of bidPrice to protect user
    # Stripe does not take decimals!
    value = int(autoWin * 100 / 2)

    print(value)
    try:
        # Charging the customer
        stripe.Charge.create(
            amount=value,
            currency="cad",
            customer=account_queryset.stripe_id,
        )
        sendMail(user.email, user.first_name)

        messages.success(
            request, 'Congratulations! You have won the auction!')
        Property.objects.filter(propertyID=propertyID).update(
            status="inactive", tenantID=userID)
        return redirect('/property/' + str(propertyID))
    except:
        messages.error(
            request, "Something went wrong, unable to charge credit card")
        return redirect('/property/' + str(propertyID))

def sendMail(email, first):

    fields = {
        'email': email,
        'first_name': first,
    }

    message_plain = render_to_string('email/auction-won.txt', fields)
    message_html = render_to_string('email/auction-won.html', fields)
    subject_title = "Congratulations! You've just won an auction"

    try:
        send_mail(
            subject_title,
            message_plain,
            settings.EMAIL_HOST_USER,
            # replce with email from params
            ['kennykitchan@gmail.com'],
            # Allows us to send HTML template emails
            html_message=message_html,
        )
    except:
        print("Email unable to send")
