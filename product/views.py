from .models import Product, StateShippingCost, RelatedProduct, VariantsCombination
from category.models import Category
import json
from contants import media_files_domain
import requests
from django.http import JsonResponse
from django.conf import settings
import time
from django.utils.translation import gettext as _
from .serialiers import SearchedProductTypeASerializer, SearchedProductDetailedSerializer
from django.db.models import F
from django.db.models.functions import Length
from django.db.models import F
from django.core.paginator import Paginator, EmptyPage
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from functions import custom_slugify


@api_view(['POST'])
def initiate_product(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        store = request.user.stores.get(id=data['store_id'])
        non_available_products = Product.objects.filter(store=store, is_available=False)
        if non_available_products.exists():
            product = non_available_products.last()
            return JsonResponse({'product_id': product.id}, status=200)
        else:
            product = Product(
                user = store.owner,
                store = store
            )
            product.save()
            product.slug = str(product.id)
            data = {
                'product_id' : product.id,
                'store_id' : store.id,
                'user_id': request.user.id,
                'MESSAGING_KEY' : settings.MESSAGING_KEY
            }
            print(data)
            try:
                receiver_url = media_files_domain + '/make-product-directory'
                response = requests.post(receiver_url, data=data)
                if response.ok: 
                    product.save()
                    return JsonResponse({'product_id': product.id}, status=200)
                else:
                    product.delete()
                    raise

            except Exception as e:
                product.delete()
                print(e)
                return JsonResponse({'detail': 'Product could not be initiated'}, status=500)
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_gallery(request):
    if request.method == 'POST':
        
        data = json.loads(request.body)
        product_id = data.get('product_id')
        gallery_images = data.get('gallery_images')
        product = request.user.products.get(id=product_id)
        product.gallery_images = json.dumps(gallery_images) if gallery_images else None
        product.image = f'{media_files_domain}/resize?width=300&url=' + gallery_images[0] if gallery_images else None
        product.save()

        receiver_url = media_files_domain + '/save-galley-images'
        data = json.dumps({
            'gallery_images': gallery_images,
            'MESSAGING_KEY' : settings.MESSAGING_KEY,
            'product_id': product_id,
            'user_id': request.user.id
        })

        print(receiver_url)
        response = requests.post(receiver_url, data={
            'data': data
        })
        if response.ok:
            return JsonResponse({'detail': 'Success'}, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_product(request):
    
    data = json.loads(request.body)
    product_id= data.get('productId') #
    product = request.user.products.get(id=product_id)

    try:
        title = data.get('title').strip()#
        if len(title) < 3:
                return JsonResponse({
                    'detail': _('Title too short'),
                    'reason': 'title',
                }, status=400)
        
        slug = data.get('slug').strip()
        if not slug:
            slug = custom_slugify(title)

        mini_description = data.get('miniDescription') #
        selected_categories= data.get('selectedCategories')#
        price = data.get('price') #
        original_price = data.get('originalPrice') #
        discount = data.get('discount') #
        shipping_cost_by_state = data.get('shippingCostByState')#
        ask_for_address = data.get('askForAddress') or False
        variants = data.get('variants') #
        prices_and_images_list = data.get('pricesAndImagesList') #
        variants_combinations = data.get('variantsCombinations')
        rich_text = data.get('richText') #
        all_products_related = data.get('allProductsRelated') or False #
        related_products = data.get('relatedProducts') #
        gallery_images= json.loads(product.gallery_images) if product.gallery_images else None
        quantity = data.get('quantity')
        sku = data.get('sku')

        new_data={}

        new_data['quantity'] = quantity
        product.quantity = quantity
        new_data['sku'] = sku
        product.sku = sku

        new_data['productId'] = product.id
        product.title = title
        new_data['title'] = title

        product.slug = slug
        new_data['slug'] = slug

        product.ask_for_address = ask_for_address
        new_data['askForAddress'] = ask_for_address

        if all_products_related:
            product.all_products_related = all_products_related
            new_data['allProductsRelated'] = all_products_related
        elif related_products:
            order = 1
            new_related_products=[]
            for id in related_products:
                related_product = Product.objects.get(user=request.user, id=id)
                RelatedProduct.objects.create(
                    order= order,
                    related_product= related_product,
                    main_product=product
                )
                new_related_products.append({
                    'reverseOrder': order,
                    'id': id,
                    'image': related_product.image,
                    'title': related_product.title
                })
                order +=1

            related_products = new_related_products
            new_data['relatedProducts'] = related_products

        if prices_and_images_list:
            new_data['pricesAndImagesList'] = prices_and_images_list
            new_data['variants'] = variants

            product.variants = variants      
            for (key, value) in variants_combinations.items():
                key = int(key)
                VariantsCombination.objects.create(
                    index=key,
                    product=product,
                    combination = value,
                    image = prices_and_images_list[key]['image'],
                    price = prices_and_images_list[key]['price'],
                    original_price = prices_and_images_list[key]['originalPrice'],
                )
            product.has_variants = True
            
            product.max_index = len(prices_and_images_list)


        if discount:
            product.discount = discount
            new_data['discount'] = discount

        if gallery_images:
            new_data['galleryImages'] = gallery_images
        
        if mini_description:
            product.mini_description = mini_description
            new_data['miniDescription'] = mini_description

        if price:
            product.price = price or None
            new_data['price'] = price
        
        if original_price:
            product.original_price = original_price or None
            new_data['originalPrice'] = original_price

        if rich_text:
            new_data['richText'] = rich_text
            product.rich_text = rich_text

        if selected_categories:
            selected_categories = Category.objects.filter(user=request.user, id__in = selected_categories)
            product.selected_categories.set(selected_categories) 
            selected_categories = list(selected_categories.values('id', 'label'))
            new_data['selectedCategories'] = selected_categories
        
        for elem in shipping_cost_by_state:
            if elem['cost'] != None or elem['costToHome'] != None:
                StateShippingCost.objects.create(
                    state_id = elem['id'],
                    cost = elem['cost'],
                    cost_to_home = elem['costToHome'],
                    product = product
                )
        new_data['shippingCostByState'] = shipping_cost_by_state

        product_files_data = json.dumps({
            'product_data': new_data,
            'images_urls' : data.pop('imagesUrls'),
            'MESSAGING_KEY' : settings.MESSAGING_KEY,
            'product_id': product_id,
        })
        
        receiver_url = media_files_domain + '/save-product'
        response = requests.post(receiver_url, data={
            'product_files_data': product_files_data
        })
        if not response.ok:
            raise
        product.is_available = True
        product.save()
        return JsonResponse({
                'detail': _('Your product was listed successfully'),
            }, status=200)
    except Exception as e:
        product.selected_categories.clear()
        product.states_shipping_cost.all().delete()
        product.related_products.all().delete()
        return JsonResponse({
                'detail': _('your Product was not listed'),
            }, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_product(request):
    
    data = json.loads(request.body)
    product_id= data.get('productId') #
    product = request.user.products.get(id=product_id)

    try:
        title = data.get('title').strip()#
        if len(title) < 3:
                return JsonResponse({
                    'detail': _('Title too short'),
                    'reason': 'title',
                }, status=400)
        
        slug = data.get('slug').strip()
        if not slug:
            slug = custom_slugify(title)

        mini_description = data.get('miniDescription') #
        selected_categories= data.get('selectedCategories')#
        price = data.get('price') #
        original_price = data.get('originalPrice') #
        discount = data.get('discount') #
        shipping_cost_by_state = data.get('shippingCostByState')#
        ask_for_address = data.get('askForAddress') or False
        variants = data.get('variants') #
        prices_and_images_list = data.get('pricesAndImagesList') #
        variants_combinations = data.get('variantsCombinations')
        
        
        rich_text = data.get('richText') #
        all_products_related = data.get('allProductsRelated') or False #
        related_products = data.get('relatedProducts') #
        gallery_images= json.loads(product.gallery_images) if product.gallery_images else None
        quantity = data.get('quantity')
        sku = data.get('sku')

        new_data={}

        new_data['quantity'] = quantity
        product.quantity = quantity
        new_data['sku'] = sku
        product.sku = sku

        product.quantity = int(data.get('quantity')) if data.get('quantity') else None
        product.sku = data.get('sku')

        new_data['productId'] = product.id
        product.title = title
        new_data['title'] = title

        product.slug = slug
        new_data['slug'] = slug

        product.ask_for_address = ask_for_address
        new_data['askForAddress'] = ask_for_address

        if all_products_related:
            product.all_products_related = all_products_related
            new_data['allProductsRelated'] = all_products_related

        elif related_products:
            order = 1
            new_related_products=[]
            RelatedProduct.objects.filter(main_product=product).exclude(id__in = related_products).delete()
            for id in related_products:
                related_product_product = Product.objects.get(user=request.user, id=id)
                [related_product, is_created] = RelatedProduct.objects.get_or_create(
                    related_product= related_product_product,
                    main_product=product
                )
                related_product.order = order
                related_product.save()

                new_related_products.append({
                    'reverseOrder': order,
                    'id': id,
                    'image': related_product_product.image,
                    'title': related_product_product.title
                })
                order +=1

            related_products = new_related_products
            new_data['relatedProducts'] = related_products

        if prices_and_images_list:
            new_data['pricesAndImagesList'] = prices_and_images_list
            new_data['variants'] = variants
            
            product.variants = variants

            combinations = product.variants_combinations.all()
            indexes = []
            for (key, value) in variants_combinations.items():
                key = int(key)
                [combination, created] = combinations.get_or_create(
                    index=key,
                    product=product,
                )
                combination.combination = value
                combination.image = prices_and_images_list[key]['image']
                combination.price = prices_and_images_list[key]['price']
                combination.original_price = prices_and_images_list[key]['originalPrice']
                combination.save()
                indexes.append(key)
            combinations.exclude(index__in = indexes).delete()
            product.has_variants = True
            product.max_index = len(prices_and_images_list)

        else:            
            product.variants = None
            product.variants_combinations.all().delete()
            product.has_variants = False

        if discount:
            product.discount = discount
            new_data['discount'] = discount

        if gallery_images:
            new_data['galleryImages'] = gallery_images
        
        if mini_description:
            product.mini_description = mini_description
            new_data['miniDescription'] = mini_description

        if price:
            product.price = price or None
            new_data['price'] = price
        
        if original_price:
            product.original_price = original_price or None
            new_data['originalPrice'] = original_price

        if rich_text:
            new_data['richText'] = rich_text
            product.rich_text = rich_text

        if selected_categories:
            selected_categories = Category.objects.filter(user=request.user, id__in = selected_categories)
            product.selected_categories.set(selected_categories) 
            selected_categories = list(selected_categories.values('id', 'label'))
            new_data['selectedCategories'] = selected_categories
        
        allStateShippingCosts = StateShippingCost.objects.filter(product = product)
        allStateShippingCosts.exclude(state_id__in = [x['id'] for x in shipping_cost_by_state]).delete()
        for elem in shipping_cost_by_state:
            if elem['cost'] != None or elem['costToHome'] != None:
                [shipping_cost, is_created] = allStateShippingCosts.get_or_create(
                    state_id = elem['id'],
                    product=product
                )
                shipping_cost.cost = elem['cost']
                shipping_cost.cost_to_home = elem['costToHome']
                shipping_cost.save()
            else:
                try:
                    shipping_cost = allStateShippingCosts.get(
                        state_id = elem['id'],
                    )
                    shipping_cost.delete()
                except:
                    pass
                shipping_cost_by_state = [d for d in shipping_cost_by_state if d.get("id") != elem['id']]

        new_data['shippingCostByState'] = shipping_cost_by_state
        product_files_data = json.dumps({
            'product_data': new_data,
            'images_urls' : data.pop('imagesUrls'),
            'MESSAGING_KEY' : settings.MESSAGING_KEY,
            'product_id': product_id,
        })
        
        receiver_url = media_files_domain + '/save-product'
        response = requests.post(receiver_url, data={
            'product_files_data': product_files_data
        })
        
        product.is_available = True
        product.save()
        return JsonResponse({
                'detail': _('Your product was updated successfully'),
            }, status=200)
    except Exception as e:
        raise
        return JsonResponse({
                'detail': _('your Product was not updated'),
            }, status=400)

@api_view(['POST'])
def incerement_product_views(request):
    data = json.loads(request.body)
    product = Product.objects.get(id = data.get('product_id'))
    product.views += 1
    product.save()
    return JsonResponse({'detail': 'success'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_products(request):
    
    search_text = request.GET.get('search-text')
    store_id = request.GET.get('store_id')
    searched_products = Product.objects.filter(user=request.user, store_id=store_id, title__icontains = search_text, is_available=True).annotate(text_length=Length('title')).order_by('title')[:10]
    serialized = SearchedProductTypeASerializer(searched_products, many=True).data
    return Response(serialized, status=200)

@api_view(['GET'])
def get_related_products(request):
    
    product = Product.objects.get(id=request.GET.get('product_id'))
    if product.all_products_related:
        related_products = Product.objects.filter(user=product.user, is_available=True).exclude(id = product.id).order_by('-id')[:20]
        related_products_list = list(related_products.annotate(index=F('id')).values('id', 'index', 'slug', 'image', 'price', 'title'))
    else:
        related_products = RelatedProduct.objects.filter(main_product = product, main_product__is_available=True)
        related_products_list = list(related_products.annotate(
            slug=F('related_product__slug'),
            image=F('related_product__image'),
            price=F('related_product__price'),
            title=F('related_product__title'),
            index=F('order')).values('id', 'index', 'slug', 'image', 'price', 'title'))
    return JsonResponse(related_products_list, safe=False, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_products_for_seller(request):
    data = json.loads(request.body)
    page_number = data.get('page')
    product_list = Product.objects.filter(user=request.user, is_available=True, store_id=data.get('store_id')).order_by('-id')  # Get all products from the database
    paginator = Paginator(product_list, 10)  # Show 10 products per page
    try:
        products = paginator.page(page_number)  # Get products for the desired page
    except EmptyPage:
        products = paginator.page(paginator.num_pages)  # If page is out of range, deliver last page of results.

    serialized = SearchedProductDetailedSerializer(products, many=True).data
    return Response({
        'products': serialized,
        'numPages': paginator.num_pages,
        'hasNext': products.has_next(),
        'hasPrev': products.has_previous(),

    }, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_product_variants(request):
    
    product = request.user.products.get(id= request.GET.get('product_id'))
    if product.variants:
        variants ={}
        for item in product.variants.values():
            variants[item['name']] = item['options']['1']['label']
    else:
        variants = None

    price = product.price
    original_price = product.original_price
    return JsonResponse({
        'variants' : variants,
        'price': price,
        'originalPrice': original_price
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_product_state(request):
    data = json.loads(request.body)
    product = Product.objects.get(
        user= request.user,
        id = data.get('product_id')
    )
    product.active = not product.active
    data = {
        'product_id' : product.id,
        'MESSAGING_KEY' : settings.MESSAGING_KEY,
        'active': product.active
    }
    receiver_url = media_files_domain + '/toggle-product-state'
    response = requests.post(receiver_url, data=data)
    if not response.ok:
        raise

    product.save()
    return JsonResponse({
        'active': product.active
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_product(request):
    data = json.loads(request.body)
    product = Product.objects.get(
        user= request.user,
        id = data.get('product_id')
    )
    product.delete()
    return JsonResponse({
        'detail': _('Your product was deleted succefully')
    })