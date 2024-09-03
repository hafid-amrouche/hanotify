from rest_framework import serializers
from user.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from contants import stores_domain
from store.serializers import StateCostSerializer

class UserSerializerWithToken(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name' ,'email', 'is_staff', 'token', 'refresh', 'storeLogo', 'shippingCosts', 'storeId', 'domain']

    token = serializers.SerializerMethodField(read_only=True)
    def get_token(self, obj):
        access_token = str(RefreshToken.for_user(obj).access_token)
        return access_token
    
    refresh = serializers.SerializerMethodField(read_only=True)
    def get_refresh(self, obj):
        refresh_token = str(RefreshToken.for_user(obj))
        return refresh_token
    
    full_name = serializers.SerializerMethodField(read_only=True)
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    storeLogo = serializers.SerializerMethodField(read_only=True)
    def get_storeLogo(self, obj):
        return 'https://upload.wikimedia.org/wikipedia/commons/c/cd/Facebook_logo_%28square%29.png'
    
    shippingCosts = serializers.SerializerMethodField(read_only=True)
    def get_shippingCosts(self, obj):
        store = obj.stores.first()
        return StateCostSerializer(store.shipping_costs.all(), many=True).data
    
    storeId = serializers.SerializerMethodField(read_only=True)
    def get_storeId(self, obj):
        return obj.stores.first().id
    
    domain = serializers.SerializerMethodField(read_only=True)
    def get_domain(self, obj):
        store = obj.stores.first()
        return store.domain.domain