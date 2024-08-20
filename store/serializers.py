from rest_framework import serializers
from .models import StateShippingCost

class StateCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = StateShippingCost
        fields = ['id', 'cost', 'costToHome']
    
    id = serializers.SerializerMethodField(read_only=True)
    def get_id(self, obj):
        return obj.state.id
    
    costToHome = serializers.SerializerMethodField(read_only=True)
    def get_costToHome(self, obj):
        return obj.cost_to_home