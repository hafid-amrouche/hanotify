from rest_framework.decorators import api_view
import json
from django.http import JsonResponse
from .models import Category, Store
from contants import media_files_domain
from django.conf import settings
import requests
from django.utils.translation import gettext as _
from functions import custom_slugify
from django.db.models import F



# Create your views here.
@api_view(['POST'])
def add_category(request):
    data = json.loads(request.body)
    title = data.get('title').strip()
    if not title:
        return JsonResponse({
            'message': 'Title is not valid'
        }, status=400)
    slug = data.get('slug').strip()
    description = data.get('description')
    image = data.get('image')
    store_id = data.get('store_id')
    store= request.user.stores.get(id=store_id)
    if Category.objects.filter(store= store, label__iexact= title).exists():
        return JsonResponse({
            'detail': _('This name is already used'),
            'field': 'name'
        }, status=400)
        
    slug = slug or custom_slugify(title)

    if Category.objects.filter(store= store, slug= slug).exists():
        return JsonResponse({
            'detail': _('This slug is already used'),
            'field': 'slug'
        }, status=400)
    
    category = Category.objects.create(
        store= store,
        user=request.user,
        label= title,
        description= description,
        image=image,
        slug= slug,
    )

    receiver_url = media_files_domain + '/save-category'
    data = json.dumps({
        'category_id': category.id,
        'category_image': image,
        'store_id': store.id,
        'MESSAGING_KEY' : settings.MESSAGING_KEY,
    })
    
    response = requests.post(receiver_url, data={
        'data': data
    })
    if not response.ok:
        category.delete()
        return JsonResponse({
            'detail': _('Category was not created')
        }, status=400)
    
    return JsonResponse({
        'categoryId': category.id
    }, status=200)


@api_view(['POST'])
def update_category(request):
    data = json.loads(request.body)
    title = data.get('title').strip()
    if not title:
        return JsonResponse({
            'message': 'Title is not valid'
        }, status=400)
    slug = data.get('slug').strip()
    description = data.get('description')
    image = data.get('image')
    store_id = data.get('store_id')
    category_id =data. get('category_id')
    store= request.user.stores.get(id=store_id)
    if Category.objects.filter(store= store, label__iexact= title).exclude(id=category_id).exists():
        return JsonResponse({
            'detail': _('This name is already used'),
            'field': 'name'
        }, status=400)
    category = Category.objects.get(
        id=category_id,
        store= store,
        user=request.user,
    )
    category.label= title
    category.description= description
    category.image=image
    slug= slug or custom_slugify(title)

    if Category.objects.filter(store= store, slug= slug).exclude(id=category_id).exists():
        return JsonResponse({
            'detail': _('This slug is already used'),
            'field': 'slug'
        }, status=400)
    
    category.slug = slug
    receiver_url = media_files_domain + '/update-category'
    data = json.dumps({
        'category_id': category.id,
        'category_image': image,
        'store_id': store.id,
        'MESSAGING_KEY' : settings.MESSAGING_KEY,
    })
    response = requests.post(receiver_url, data={
        'data': data
    })

    if not response.ok:
        return JsonResponse({
            'detail': _('Category was not updated')
        }, status=400)

    category.save()
    return JsonResponse({
        'catgeoryId': category.id
    }, status=200)

# Create your views here.
@api_view(['POST'])
def delete_category(request):
    data = json.loads(request.body)
    store= request.user.stores.get(id=data.get('store_id'))
    category = store.categories.get(id=data.get('category_id'))
    receiver_url = media_files_domain + '/delete-category'
    data = json.dumps({
        'category_id': category.id,
        'store_id': store.id,
        'MESSAGING_KEY' : settings.MESSAGING_KEY,
    })
    try:
        response = requests.post(receiver_url, data={
            'data': data
        })
        category.delete()
        return JsonResponse({
            'detail': 'Success'
        }, status=200)
    except:
        return JsonResponse({
            'detail': _('Category was not deleted')
        }, status=400)
    
@api_view(['GET'])
def get_categories(request):
    return JsonResponse(list(request.user.categories.values('id', 'label', 'image', 'slug', 'description', 'id')), safe=False )




# hanotify-store
def serialized_searched_products(query):
    return list(query.values('id', 'slug', 'image', 'price', 'original_price', 'title'))

def serialized_category_preview_products(query):
    return list(
        query.annotate(
            product_id = F('id'),
        ).values('product_id','image', 'price', 'title', 'slug', 'original_price'))


@api_view(['GET'])
def category_page(request):

    domain = request.GET.get('domain')  
    store = Store.objects.get(domain__domain = domain)  
    slug = request.GET.get('slug') 
    section = store.home_page.sections.get(section_id=slug)
    if section.show_latest_products :
        if section.category:
            products = section.category.products.all()[:20]
        else:
            products = store.products.all()[:20]
            
    else:
        products = section.products.all()[:20]


    return JsonResponse({
        'products' : serialized_category_preview_products(products),
        'title': section.title
    })
