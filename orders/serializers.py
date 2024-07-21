from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    # token = serializers.SerializerMethodField(read_only=True)
    # def get_token

    class Meta:
        model = Order
        fields= [
            'product',
            'full_name',
            'phone_number',
            'created_at',
            'state',
            'city',
            'address',
            'quantity',
            'home_delevery',
            'is_abandoned',
            'status'
        ]
