from rest_framework import serializers

from .models import Bidlet

class BidletSerializer(serializers.ModelSerializer):
	class Meta:
		model = Bidlet
		fields = ('property', 'owner')
