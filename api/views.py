from rest_framework import generics

from .models import Bidlet
from .serializers import BidletSerializer

class BidletList(generics.ListCreateAPIView):
	"""
	API endpoint for listing and creating bid objects
	"""
	queryset = Bidlet.objects.all()
	serializer_class = BidletSerializer
	print(queryset[0].id)
	print(queryset[0].property)
	print(queryset[0].owner)

class UserList(generics.ListCreateAPIView):

	print("Kenny")
	queryset = Bidlet.objects.all()
	serializer_class = BidletSerializer
