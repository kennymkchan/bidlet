# Use this command to run
# cmd.exe /c "python manage.py shell < cron/cron.py"
import stripe
from api.models import Property, Bidding, Bidders
from users.models import Account
from datetime import datetime, timedelta
from django.conf import settings

currentTime = datetime.now()
pastHour = currentTime - timedelta(hours=1)

biddingObj = Bidding.objects.filter(dateEnd__range=(pastHour, currentTime))

# sublets should contain a list of unique property id
for bid in biddingObj:
    bidder = Bidders.objects.filter(biddingID=bid.biddingID).last()
    # Bidder could be none if no one has bid on the property before
    try:
        userID = bidder.userID
        property_queryset = Property.objects.filter(
            propertyID=bid.propertyID).exclude(status="inactive").first()
        account_queryset = Account.objects.get(user_id=userID)
        amount = property_queryset.curPrice
        stripe.api_key = settings.STRIPE_KEY
        value = int(amount * 100 / 2)
        try:
            stripe.Charge.create(
                amount=value,
                currency="cad",
                customer=account_queryset.stripe_id,
            )
            Property.objects.select_for_update().filter(propertyID=bid.propertyID).update(tenantID=userID, status="inactive")
        except:
            pass
    except:
        pass

# Set all these properties to inactive
# property_queryset.update(status="inactive")
