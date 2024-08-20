from rest_framework import serializers
from .models import Product

class SearchedProductTypeASerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'image', 'title']

class SearchedProductDetailedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'image', 'title', 'price', 'active', 'views', 'quantity', 'slug']