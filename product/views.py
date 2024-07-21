from .models import Product
import json
from contants import media_files_domain
import requests
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.conf import settings

from rest_framework.decorators import api_view


main_user = User.objects.get(id=1)

@api_view(['POST'])
def initiate_product(request):
    if request.method == 'POST':
        receiver_url = media_files_domain + '/make-product-directory'
        product = Product.objects.create(
            user = request.user
        )
        data = {
            'product_id' : product.id,
            'user_id': request.user.id,
            'MESSAGING_KEY' : settings.MESSAGING_KEY
        }
        
        try:
            response = requests.post(receiver_url, data=data)
            response_data = response.json()  # Assuming the response is JSON
            return JsonResponse({'product_id': product.id}, status=200)

        except Exception as e:
            print(e)
            return JsonResponse({'detail': 'Product could not be initiated'}, status=500)

# Create your views here.


