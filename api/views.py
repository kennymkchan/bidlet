from rest_framework import generics
from django.shortcuts import render

from .models import Bidlet
from .serializers import BidletSerializer
from django.contrib.auth.decorators import login_required

class BidletList(generics.ListCreateAPIView):
	queryset = Bidlet.objects.all()
	serializer_class = BidletSerializer
