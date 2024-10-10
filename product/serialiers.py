from rest_framework import serializers
from .models import Product

class SearchedProductTypeASerializer(serializers.ModelSerializer):
    product_id = serializers.SerializerMethodField(read_only=True)
    def get_product_id(self, obj):
        return obj.id
    class Meta:
        model = Product
        fields = ['product_id', 'image', 'title']

class SearchedProductDetailedSerializer(serializers.ModelSerializer):
    product_id = serializers.SerializerMethodField(read_only=True)
    def get_product_id(self, obj):
        return obj.id
    class Meta:
        model = Product
        fields = ['product_id', 'image', 'title', 'price', 'active', 'views', 'quantity', 'slug']

class ProductSerializerA(serializers.ModelSerializer):
    product_id = serializers.SerializerMethodField(read_only=True)
    def get_product_id(self, obj):
        return obj.id
    class Meta:
        model = Product
        fields = ['product_id', 'image', 'price', 'title']