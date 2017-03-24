from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from django.views.generic import TemplateView

from users.views import (
    login_view,
    logout_view,
    registration_view,
    home_view,
    profile_edit_view,
    )

from api.views import (
    createBid,
    createProperty,
    propertyDetails,
    Listings,
    searchListings,
    )

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', TemplateView.as_view(template_name='index.html')),

    # Property Management
	url(r'^search/', searchListings.as_view(), name='search-listings'),
	url(r'^listings/', Listings.as_view(), name='listings'),
	url(r'^property/(?P<id>\d{1,})/$', propertyDetails.as_view(), name='property'),
	url(r'^createProperty/', createProperty, name='create-property'),

    # Budding Management
    url(r'^bid/(?P<propertyID>\d{1,})', createBid, name='create-bid'),

    # Accounts
    url(r'^login/', login_view, name="login"),
    url(r'^logout/', logout_view, name="logout"),
    url(r'^register/', registration_view, name="register"),
    url(r'^home/', home_view, name="home"),
    url(r'^user/edit', profile_edit_view, name="edit_profile"),
]
