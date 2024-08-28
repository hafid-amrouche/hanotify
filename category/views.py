from rest_framework.decorators import api_view
import json
from django.http import JsonResponse
import time
from .models import Category
from contants import media_files_domain
from django.conf import settings
import requests
from django.utils.translation import gettext as _
from functions import custom_slugify



# Create your views here.
@api_view(['POST'])
def addCategory(request):
    time.sleep(1)
    data = json.loads(request.body)
    title = data.get('title').strip()
    if not title:
        return JsonResponse({
            'message': 'Title is not valid'
        }, status=400)
    slug = data.get('slug').strip()
    description = data.get('description')
    image = data.get('image')
    store= request.user.stores.first()
    category = Category.objects.create(
        store= store,
        user=request.user,
        label= title,
        description= description,
        image=image,
        slug= slug or custom_slugify(title),
    )

    receiver_url = media_files_domain + '/files/save-category'
    data = json.dumps({
        'category_id': category.id,
        'category_image': image,
        'store_id': store.id,
        'MESSAGING_KEY' : settings.MESSAGING_KEY,
    })
    try:
        response = requests.post(receiver_url, data={
            'data': data
        })
        return JsonResponse({
            'catgeoryId': category.id
        }, status=200)
    except:
        category.delete()
        return JsonResponse({
            'detail': _('Category was not created')
        }, status=400)


    
    
@api_view(['GET'])
def get_categories(request):
    time.sleep(2)
    return JsonResponse(list(request.user.categories.values('id', 'label', 'image')), safe=False )
