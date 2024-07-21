from .models import Order
import json
from .serializers import OrderSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated



# Create your views here.
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_orders(request):
    smallest_id = request.GET.get('smallest_id')
    largest_id = request.GET.get('largest_id')
    if smallest_id and largest_id:
        orders = Order.objects.exclude(id__gte = smallest_id, id__lte=largest_id)
    else:
        orders = Order.objects.all()
    is_next = orders.count() > 20 
    orders = orders.order_by('-created_at')[:20]
    ordersJson = OrderSerializer(orders, many=True).data
    return Response({
        'orders' : ordersJson,
        'isNext' : is_next
    })

    