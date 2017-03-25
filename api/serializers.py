from rest_framework import serializers

from .models import Property, Bidding, Bidders

class PropertySerializer(serializers.ModelSerializer):
	class Meta:
		model = Property
		fields = (
			'propertyID',
			'title',
			'description',
			'ownerID',
			'address',
			'country',
			'city',
			'postalCode',
			'suite',
			'image',
			'startPrice',
			'curPrice',
			'biddingID',
			'availStart',
			'availEnd',
			'rooms'
			)

class BiddingSerializer(serializers.ModelSerializer):
	class Meta:
		model = Bidding
		fields = (
			'biddingID',
			'propertyID',
			'startPrice',
			'curPrice',
			'ownerID',
			'dateStart',
			'dateEnd'
			)

class BiddersSerializer(serializers.ModelSerializer):
	class Meta:
		model = Bidders
		fields = (
			'biddingID',
			'userID',
			'bidPrice'
			)
