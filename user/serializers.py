from rest_framework import serializers
from user.models import User
from rest_framework_simplejwt.tokens import RefreshToken

class UserSerializerWithToken(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name' ,'email', 'is_staff', 'token', 'refresh']

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