from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.BidletList.as_view(), name='bidlet-list'),
	url(r'^search/', views.searchListings.as_view(), name='search-listings'),
	url(r'^listings/', views.Listings.as_view(), name='listings'),
	url(r'^property/(?P<id>\d{1,})/$', views.propertyDetails.as_view(), name='property'),
	url(r'^bid/(?P<propertyID>\d{1,})', views.createBid, name='create-bid'),
	url(r'^createProperty/', views.createProperty, name='create-property'),
	url(r'^secondary/', views.UserList.as_view(), name='user-list'),
]
