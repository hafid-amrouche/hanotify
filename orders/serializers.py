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
        return order.shipping_city.name if order.shipping_city else None

    shipping_city_id = serializers.SerializerMethodField(read_only=True)
    def get_shipping_city_id(self, order):
        return order.shipping_city_id if order.shipping_city else None
    
    shipping_state_id = serializers.SerializerMethodField(read_only=True)
    def get_shipping_state_id(self, order):
        return order.shipping_state_id if order.shipping_state_id else None
    
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
            'shipping_state_id',
            'shipping_city_id',
            'made_by_seller',
            'seller_note',
            'client_note'
        ]

class AbndonedOrderPreviewSerializer(serializers.ModelSerializer):
    
    shippingState = serializers.SerializerMethodField(read_only=True)
    def get_shippingState(self, order):
        return order.shipping_state.name if order.shipping_state else '------'
    
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
        return order.shipping_city.name if order.shipping_city else None


    phone_number = serializers.SerializerMethodField(read_only=True)
    def get_phone_number(self, order):
        return order.phone_number if order.show_phone_number else 'locked'
    
    shipping_city_id = serializers.SerializerMethodField(read_only=True)
    def get_shipping_city_id(self, order):
        return order.shipping_city_id if order.shipping_city else None
    
    shipping_state_id = serializers.SerializerMethodField(read_only=True)
    def get_shipping_state_id(self, order):
        return order.shipping_state_id if order.shipping_state_id else None
    
    class Meta:
        model = Order
        fields= [
            'id',
            'product',
            'created_at',
            'full_name',
            'shippingState',
            'status', # order from ordering and indexing
            'product_quantity',
            'shipping_to_home',
            'shippingCity',
            'shipping_address',
            'shipping_state_id',
            'shipping_city_id',
            'made_by_seller',
            'phone_number',
            'seller_note',
            'client_note'
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
