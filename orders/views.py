from .models import Order
import json
from .serializers import OrderPreviewSerializer, OrderDetailsSerializer, AbndonedOrderPreviewSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from product.models import Product, StateShippingCost
from others.models import State, City
from django.http import JsonResponse
from functions import get_client_ip, generate_token_from_id
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage
from time import sleep
from store.models import Visitor, IpAddress,Store, VIPStore
from django.db.models import Q
from store.models import Status
from django.utils.translation import gettext as _





# Create your views here.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orders(request):
    
    data = request.GET
    page_number = data.get('page')
    store = request.user.stores.get(id = data.get('store_id'))
    filter_criteria = Q(store=store) & Q(is_abandoned=False)
   
    search_text = data.get('search_text')
    if (search_text):
        if search_text.isdigit():
            filter_criteria = filter_criteria & ( Q(phone_number__icontains = search_text)| Q(id = search_text))
        else:
            filter_criteria = filter_criteria & (Q(product__title__icontains = search_text) | Q(full_name__icontains = search_text))
        
    

    date = data.get('date')
    if date:
        if date == '1-day':
            delta = timezone.now() - timezone.timedelta(days=1)
            
            
        elif date == '7-days':
            delta = timezone.now() - timezone.timedelta(days=7)
            
        elif date == '1-month':
            delta = timezone.now() - timezone.timedelta(days=30)

        elif date == '1-year':
            delta = timezone.now() - timezone.timedelta(days=365)

        filter_criteria = filter_criteria & Q(created_at__gte = delta)
    
    orders = Order.objects.filter(filter_criteria).order_by('-id')  # Get all products from the database
    
    orders_per_page = int(data.get('orders_per_page'))
    paginator = Paginator(orders, orders_per_page)  # Show 10 products per page
    try:
        orders = paginator.page(page_number)  # Get products for the desired page
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)  # If page is out of range, deliver last page of results.

    response = {
        'statusList': list(store.statuses.values('id', 'text', 'icon')) if data.get('status_list_fetched') == 'false' else None,
        'numPages': paginator.num_pages,
        'hasNext': orders.has_next(),
        'hasPrev': orders.has_previous(),
        'orders':  OrderPreviewSerializer(orders, many=True).data

    }

    return Response(response, status=200)

# Create your views here.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_abandoned_orders(request):
    
    data = request.GET
    page_number = data.get('page')
    store = request.user.stores.get(id = data.get('store_id'))
    filter_criteria = Q(store=store) & Q(is_abandoned=True)
   
    search_text = data.get('search_text')
    if (search_text):
        if search_text.isdigit():
            filter_criteria = filter_criteria & ( Q(phone_number__icontains = search_text)| Q(id = search_text))
        else:
            filter_criteria = filter_criteria & (Q(product__title__icontains = search_text) | Q(full_name__icontains = search_text))
        
    

    date = data.get('date')
    if date:
        if date == '1-day':
            delta = timezone.now() - timezone.timedelta(days=1)
            
            
        elif date == '7-days':
            delta = timezone.now() - timezone.timedelta(days=7)
            
        elif date == '1-month':
            delta = timezone.now() - timezone.timedelta(days=30)

        elif date == '1-year':
            delta = timezone.now() - timezone.timedelta(days=365)

        filter_criteria = filter_criteria & Q(created_at__gte = delta)
    
    orders = Order.objects.filter(filter_criteria).order_by('-id')  # Get all products from the database
    
    orders_per_page = int(data.get('orders_per_page'))
    paginator = Paginator(orders, orders_per_page)  # Show 10 products per page
    try:
        orders = paginator.page(page_number)  # Get products for the desired page
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)  # If page is out of range, deliver last page of results.

    response = {
        'statusList': list(store.statuses.values('id', 'text', 'icon')) if data.get('status_list_fetched') == 'false' else None,
        'numPages': paginator.num_pages,
        'hasNext': orders.has_next(),
        'hasPrev': orders.has_previous(),
        'orders':  AbndonedOrderPreviewSerializer(orders, many=True).data

    }

    return Response(response, status=200)

# Create your views here.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order(request):
    data = request.GET
    store = request.user.stores.get(id = data.get('store_id'))
    order = Order.objects.get( store=store, is_abandoned=False, id=data.get('id'))  # Get all products from the database
    serialized = OrderDetailsSerializer(order).data
    return Response({
        'order': serialized,
    }, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_abandoned_order(request):
    data = request.GET
    store = request.user.stores.get(id = data.get('store_id'))
    order = Order.objects.get( store=store, is_abandoned=True, id=data.get('id'))  # Get all products from the database
    serialized = OrderDetailsSerializer(order).data
    return Response({
        'order': serialized,
    }, status=200)


@api_view(['POST'])
def create_order(request):
    data = json.loads(request.body)
    product = Product.objects.get(id=data.get('product_id'))
    phone_number = data.get('phone_number').strip()
    len_number = len(phone_number)
    if not((len_number == 10 or len_number == 9 ) and phone_number.isdigit()):
        return JsonResponse({"detail": 'Stop playing around you\'re not a hacker'}, status= 400)
    
    state_id = data.get('state_id')
    
    shipping_state = State.objects.get(id = state_id)
    try:
        shipping_state_cost = StateShippingCost.objects.get(state = shipping_state, product=product)
    except:
        shipping_state_cost = None
    
    combination_index = data.get('combination_index')

    if product.has_variants:
        try:        
            variants_combination = product.variants_combinations.get(index = combination_index)      
            price = variants_combination.price or 0
            combination = variants_combination.combination
        except:
            price = product.variants_combinations.first().price or 0
            combination = None

    else:        
        price =product.price or 0
        combination = None

    quantity = data.get('quantity')
    shipping_to_home = data.get('shippingToHome')
    shipping_cost = shipping_state_cost and (shipping_state_cost.cost_to_home if shipping_to_home else shipping_state_cost.cost
)
    product_dict = {
        'image': product.image,
        'title': product.title,
        'price': price,
        'id': product.id,
        'shipping_cost': shipping_cost,
        'total_price': price * quantity + (shipping_cost or 0)
    }

    if combination:
        product_dict['combination'] = combination

    city_id = data.get('city_id')
    try:
        city = City.objects.get(id= city_id, state=shipping_state)
    except:
        city = shipping_state.cities.first()
    

    order = Order.objects.create(
        store= product.store,
        product = product_dict,
        full_name = data.get('full_name').strip(),
        phone_number = phone_number,
        shipping_state = shipping_state,
        shipping_city = city,
        shipping_to_home = shipping_to_home,
        created_at = timezone.now(),
        product_quantity = quantity,
        show_phone_number = VIPStore.objects.filter(store = product.store).exists()
    )
    order.token = generate_token_from_id(order.id)

    tracker = data.get('tracker')
    if tracker:
        try:
            visitor = Visitor.objects.get(store=order.store, tracker = tracker)
            visitor.last_visit = timezone.now()
            visitor.save()
            IpAddress.objects.get_or_create(
                visitor = visitor,
                ip_address = get_client_ip(request)
            )
        except:
            visitor = Visitor.objects.create(
                store=order.store,
                last_visit = timezone.now()
            )
            visitor.tracker = generate_token_from_id(visitor.id)
            visitor.save()

            IpAddress.objects.create(
                visitor = visitor,
                ip_address = get_client_ip(request)
            )
    else:
        visitor = Visitor.objects.create(
            store=order.store,
            last_visit = timezone.now()
        )
        visitor.tracker = generate_token_from_id(visitor.id)
        visitor.save()

        IpAddress.objects.create(
            visitor = visitor,
            ip_address = get_client_ip(request)
        )

    order.visitor = visitor
    order.save()
    return Response({
        'orderId' : order.id,
        'orderToken': order.token
    })

@api_view(['POST'])
def update_order(request):
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        order_token =  data.get('order_token')
        order = Order.objects.get(id=order_id, token=order_token)
        state_id = data.get('state_id')
        shipping_state = State.objects.get(id = state_id)
        full_name = data.get('full_name').strip()
        phone_number = data.get('phone_number').strip()
        city_id = data.get('city_id')

        order.full_name = full_name
        if not phone_number.isdigit():
            return JsonResponse({"detail": 'Stop playing around you\'re not a hacker'}, status= 400)
        
        try:
            city = City.objects.get(id= city_id, state=shipping_state)
        except:
            city = shipping_state.cities.first()
            
        order.phone_number = phone_number
        order.shipping_state = shipping_state
        order.shipping_city = city
        order.created_at = timezone.now()
        order.save()
        return JsonResponse({
            'orderId' : order.id,
            'orderToken': order.token
        })
   
    except Exception as e:
        print('orders/views/112 :', str(e))
        return JsonResponse({'detail' : str(e)}, status=400)
    
@api_view(['POST'])
def confirm_order(request): ## add this front end
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        order_token = data.get('order_token')
        order = Order.objects.get(id=order_id, token=order_token)
        if not order.is_abandoned:
            return JsonResponse({"datail": 'You\'re not a hacker'}, status=400)
        product = Product.objects.get(id = order.product['id'])

        tracker = data.get('tracker')
        if tracker:
            try:
                visitor = Visitor.objects.get(tracker = tracker)
                visitor.tracker = generate_token_from_id(visitor.id)
                visitor.save()
                IpAddress.objects.get_or_create(
                    visitor = visitor,
                    ip_address = get_client_ip(request)
                )
            except:
                visitor = Visitor.objects.create(
                    store=order.store,
                    last_visit = timezone.now()
                )
                visitor.tracker = generate_token_from_id(visitor.id)
                visitor.save()

                IpAddress.objects.create(
                    visitor = visitor,
                    ip_address = get_client_ip(request)
                )

        else:
            visitor = Visitor.objects.create(
                store=order.store,
                last_visit = timezone.now()
            )
            visitor.tracker = generate_token_from_id(visitor.id)
            visitor.save()

            IpAddress.objects.create(
                visitor = visitor,
                ip_address = get_client_ip(request)
            )
        order.visitor = visitor
        order.shipping_address = data.get("shipping_address")
        
        state_id = data.get('state_id')
    
        shipping_state = State.objects.get(id = state_id)
        try:
            shipping_state_cost = StateShippingCost.objects.get(state = shipping_state, product=product)
        except:
            shipping_state_cost = None

        combination_index = data.get('combination_index')

        if product.has_variants:
            try:        
                variants_combination = product.variants_combinations.get(index = combination_index)      
                price = variants_combination.price or 0
                combination = variants_combination.combination
            except:
                price = product.variants_combinations.first().price or 0
                combination = None

        else:        
            price=product.price or 0
            combination = None


        shipping_to_home = data.get('shippingToHome')
        shipping_cost = shipping_state_cost and (shipping_state_cost.cost_to_home if shipping_to_home else shipping_state_cost.cost)
        quantity = data.get('quantity')

        product_dict = {
            'image': product.image,
            'title': product.title,
            'price': price,
            'id': product.id,
            'shipping_cost': shipping_cost,
            'total_price': price * quantity + (shipping_cost or 0)
        }
    
        if combination:
            product_dict['combination'] = combination
        
        city_id = data.get('city_id')
        try:
            city = City.objects.get(id= city_id, state=shipping_state)
        except:
            city = shipping_state.cities.first()
            print('CITY ID: ' + str(city_id))
        
        full_name  = data.get('full_name').strip()
        if not full_name:
            return JsonResponse({"datail": 'Full name error'}, status=400)
        
        order.client_note= data.get('client_note')
        
        order.shipping_city = city
        order.product = product_dict
        order.is_abandoned = False
        order.show_phone_number = True
        order.product_quantity=quantity
        order.created_at = timezone.now()
        order.save()
    except Exception as e:
        raise

    return JsonResponse({"datail": 'Success'}, status=200)
    
@api_view(['POST'])
def change_orders_status(request):
    data = json.loads(request.body)
    orders_id = data.get('orders_id')
    store_id = data.get('store_id')
    status_id = data.get('status_id')
    store = request.user.stores.get(id=store_id)
    orders = Order.objects.filter(store=store, id__in=orders_id)
    status = store.statuses.get(id=status_id)
    orders.update(status=status)
    return JsonResponse({"detail": 'success'})

@api_view(['POST'])
def delete_orders(request):
    try:
        data = json.loads(request.body)
        store = Store.objects.get(owner = request.user, id= data.get('store_id'))
        orders_id = data.get('orders_ids')
        orders = store.orders.filter(id__in = orders_id)
        orders.delete()
        return JsonResponse({
            'ordersId' : orders_id
        })
    except Exception as e:
        print(e)
   
@api_view(['POST'])
def create_user_order(request): ## add this front end
    
    data = json.loads(request.body)
    phone_number = data.get('phone_number')
    if len(phone_number) < 0 or (not phone_number.isdigit()):
        return JsonResponse({"detail": _('Phone number is invalid')}, status=400)
    product_id = data.get('product_id')
    state_id = data.get('state_id')
    full_name=data.get('full_name')
    address= data.get('shipping_address')
    price = data.get('price')
    quantity = data.get('quantity')
    shipping_cost = data.get('shipping_cost')
    shipping_to_home= data.get('shipping_to_home')
    city_id = data.get('city_id')
    variants = data.get('variants')
    title = data.get('title')
    image = data.get('image')
    store_id = data.get('store_id')
    client_note= data.get('client_note')
    seller_note= data.get('seller_note')

    state = State.objects.get(id = state_id)
    store = request.user.stores.get(id = store_id)

    now = timezone.now()
    [visitor, created] = Visitor.objects.get_or_create(
        store=store,
        tracker = None,
    )

    order = Order.objects.create(
        store= request.user.stores.get(id = store_id),
        product = {
            'image': image,
            'title': title,
            'price': price,
            'id': product_id,
            'shipping_cost': shipping_cost,
            'total_price': price * quantity + (shipping_cost or 0),
            'combination': variants,
        },
        shipping_state =state,
        shipping_city = City.objects.get(state=state, id = city_id),
        shipping_address = address,
        full_name = full_name,
        phone_number = phone_number,
        created_at = now,
        shipping_to_home = shipping_to_home,
        status = Status.objects.filter(store=store).first(),
        visitor = visitor,
        product_quantity = quantity,
        is_abandoned = False,
        made_by_seller = True,
        client_note= client_note,
        seller_note= seller_note
        
    )
    
    order.token = generate_token_from_id(order.id)
    order.save()

    return JsonResponse({"order": OrderPreviewSerializer(order).data})

@api_view(['POST'])
def update_user_order(request): ## add this front end
    
    data = json.loads(request.body)
    phone_number = data.get('phone_number')
    if len(phone_number) < 0 or (not phone_number.isdigit()):
        return JsonResponse({"detail": _('Phone number is invalid')}, status=400)
    product_id = data.get('product_id')
    state_id = data.get('state_id')
    full_name=data.get('full_name')
    address= data.get('shipping_address')
    price = data.get('price')
    quantity = data.get('quantity')
    shipping_cost = data.get('shipping_cost')
    shipping_to_home= data.get('shipping_to_home')
    city_id = data.get('city_id')
    variants = data.get('variants')
    title = data.get('title')
    image = data.get('image')
    store_id = data.get('store_id')
    client_note= data.get('client_note')
    seller_note= data.get('seller_note')

    state = State.objects.get(id = state_id)
    store = request.user.stores.get(id = store_id)


    order = Order.objects.get(
        id=data.get('order_id'),
        store=store,
    )

    order.product = {
            'image': image,
            'title': title,
            'price': price,
            'id': product_id,
            'shipping_cost': shipping_cost,
            'total_price': price * quantity + (shipping_cost or 0),
            'combination': variants,
    }
    order.shipping_state =state
    order.shipping_city = City.objects.get(state=state, id = city_id)
    order.shipping_address = address
    order.full_name = full_name
    order.phone_number = phone_number
    order.shipping_to_home = shipping_to_home
    order.product_quantity = quantity
    order.client_note = client_note
    order.seller_note = seller_note
    order.save()
    return JsonResponse({"order": OrderPreviewSerializer(order).data})

@api_view(['POST'])
def reveal_phone_number(request):
    
    data = json.loads(request.body)
    store_id = data.get('store_id')
    store = request.user.stores.get(id = store_id)
    order = Order.objects.get(
        id=data.get('order_id'),
        store=store,
    )
    if not order.show_phone_number:
        order.show_phone_number = True
        order.save()
        # decrease points
        return JsonResponse({
            'phone_number': order.phone_number,
            'revelied': True
        })
    else:
        return JsonResponse({
            'phone_number': order.phone_number,
            'revelied': False
        })
