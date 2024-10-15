from .models import Product
from django.db.models.signals import pre_delete
import requests
from django.conf import settings
from contants import media_files_domain



def produt_pre_delete(sender, instance, **kwargs):
    data = {
        'store_id': instance.store.id,
        'product_id' : instance.id,
        'MESSAGING_KEY' : settings.MESSAGING_KEY,
        'user_id': instance.user.id,
    }
    receiver_url = media_files_domain + '/delete-product'
    response = requests.post(receiver_url, data=data)
    if not response.ok:
        print('error product/signals 18', response)
        print(response.text)
        raise

    

pre_delete.connect(produt_pre_delete, Product)