# Use this command to run
# cmd.exe /c "python manage.py shell < cron/cron.py"
import stripe
from api.models import Property, Bidding, Bidders
from users.models import Account
from datetime import datetime, timedelta
from django.conf import settings

currentTime = datetime.now()
pastHour = currentTime - timedelta(days=10)

biddingObj = Bidding.objects.filter(dateEnd__range=(pastHour, currentTime))

sublets = []
users = []

# sublets should contain a list of unique property id
for bid in biddingObj:
    sublets.append(bid.propertyID)
    bidder = Bidders.objects.filter(biddingID=bid.biddingID).last()
    # Bidder could be none if no one has bid on the property before
    try:
        userID = bidder.userID
        users.append(userID)
    except:
        users.append(None)

# Query a set of properties that the user is watching
property_queryset = Property.objects.filter(
    propertyID__in=sublets).exclude(status="inactive")

# Set all these properties to inactive
property_queryset.update(status="inactive")

for user, place in zip(users, property_queryset):
    if user is None:
        continue
    else:
        account_queryset = Account.objects.get(user_id=user)
        property_queryset = Property.objects.get(propertyID=place.propertyID)
        amount = property_queryset.curPrice
        stripe.api_key = settings.STRIPE_KEY
        value = int(amount * 100 / 2)
        try:
            stripe.Charge.create(
                amount=value,
                currency="cad",
                customer=account_queryset.stripe_id,
            )
            property_queryset.update(tenantID=user)
        except:
            pass
