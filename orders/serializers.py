from rest_framework import serializers
from .models import Order

class OrderPreviewSerializer(serializers.ModelSerializer):
    
    shippingState = serializers.SerializerMethodField(read_only=True)
    def get_shippingState(self, order):
        return order.shipping_state.name
    
    status=serializers.SerializerMethodField(read_only=True)
    def get_status(self, order):
        if order.status:
            return {
                'text': order.status.text,
                'icon': order.status.icon,
                'id': order.id,
            }
        else:
            return None
    
    shippingCity = serializers.SerializerMethodField(read_only=True)
    def get_shippingCity(self, order):
        return order.shipping_city.name


    
    class Meta:
        model = Order
        fields= [
            'id',
            'product',
            'created_at',
            'full_name',
            'phone_number',
            'shippingState',
            'status', # order from ordering and indexing
            'product_quantity',
            'shipping_to_home',
            'shippingCity',
            'shipping_address',
        ]

class OrderDetailsSerializer(serializers.ModelSerializer):     
    visitor = serializers.SerializerMethodField(read_only=True)
    def get_visitor(self, order):
        visitor = order.visitor
        return visitor and {
            'tracker' : visitor.tracker,
            'ip_adresses' : list(visitor.ip_addresses.values('ip_address')),
            'blocked': visitor.blocked,
            'id': visitor.id
        }
    
    class Meta:
        model = Order
        fields= [
            'visitor'
        ]
