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
from store.models import Visitor, IpAddress,Store
from django.db.models import Q
from store.models import Status
from django.utils.translation import gettext as _
from functions import send_event_to_facebook

from google.oauth2 import service_account
from googleapiclient.discovery import build
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Order
from .serializers import OrderPreviewSerializer
from django.conf import settings





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

    product_dict = {
        'image': product.image,
        'title': product.title,
        'price': price,
        'id': product.id,
        'shipping_cost': None,
        'total_price': price * quantity
    }
    if combination:
        product_dict['combination'] = combination

    order = Order.objects.create(
        store= product.store,
        product = product_dict,
        full_name = data.get('full_name').strip(),
        phone_number = phone_number,
        shipping_state = None,
        shipping_city = None,
        created_at = timezone.now(),
        product_quantity = quantity,
        show_phone_number = product.store.plan in ['type-b', 'type-c'],
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
        if state_id :
            shipping_state = State.objects.get(id = state_id)
            city_id = data.get('city_id')
            try:
                city = City.objects.get(id= city_id, state=shipping_state)
            except:
                city = shipping_state.cities.first()
            
            order.shipping_state = shipping_state
            order.shipping_city = city

        full_name = data.get('full_name').strip()
        phone_number = data.get('phone_number').strip()

        order.full_name = full_name
        if not phone_number.isdigit():
            return JsonResponse({"detail": 'Stop playing around you\'re not a hacker'}, status= 400)
        
            
        order.phone_number = phone_number
        order.created_at = timezone.now()

        order.save()
        return JsonResponse({
            'orderId' : order.id,
            'orderToken': order.token
        })
   
    except Exception as e:
        print('orders/views/112 :', str(e))
        return JsonResponse({'detail' : str(e)}, status=400)

def send_new_order_notification(store, instance):
    channel_layer = get_channel_layer()

    # Send message to the orders group
    async_to_sync(channel_layer.group_send)(
        f"orders-{store.id}",
        {
            "type": "send_new_order",
            "order": OrderPreviewSerializer(instance).data
        }
    )

def append_order_to_sheet(order_data, spreadsheet_id, sheet_name):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = settings.BASE_DIR / 'json_files/service_account.json'

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()

    values = [
        order_data  # A list of the order data, e.g., [order_id, product_name, quantity, price, ...]
    ]
    body = {
        'values': values
    }
    result = sheet.values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A2",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()
    return result

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
        ip_address = get_client_ip(request)
        if tracker:
            try:
                visitor = Visitor.objects.get(tracker = tracker)
                visitor.tracker = generate_token_from_id(visitor.id)
                visitor.save()
                IpAddress.objects.get_or_create(
                    visitor = visitor,
                    ip_address = ip_address
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
                    ip_address = ip_address
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
                ip_address = ip_address
            )
        order.visitor = visitor
        order.shipping_address = data.get("shipping_address")
        
        state_id = data.get('state_id')
        shipping_state = State.objects.get(id = state_id)
        city_id = data.get('city_id')
        try:
            city = City.objects.get(id= city_id, state=shipping_state)
        except:
            city = shipping_state.cities.first()
        
        order.shipping_state = shipping_state
        order.shipping_city = city

        try:
            shipping_state_cost = StateShippingCost.objects.get(state = shipping_state, product=product)
        except:
            shipping_state_cost = None


        shipping_to_home = data.get('shippingToHome')
        order.shipping_to_home = shipping_to_home
        shipping_cost = shipping_state_cost and (shipping_state_cost.cost_to_home if shipping_to_home else shipping_state_cost.cost)

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


        quantity = data.get('quantity')

        total_price = price * quantity + (shipping_cost or 0)
        product_dict = {
            'image': product.image,
            'title': product.title,
            'price': price,
            'id': product.id,
            'shipping_cost': shipping_cost,
            'total_price': total_price
        }
    
        if combination:
            product_dict['combination'] = combination
        
        city_id = data.get('city_id')
        try:
            city = City.objects.get(id= city_id, state=shipping_state)
        except:
            city = shipping_state.cities.first()
        
        full_name  = data.get('full_name').strip()
        if not full_name:
            return JsonResponse({"datail": 'Full name error'}, status=400)
        
        order.client_note= data.get('client_note')
        order.shipping_city = city
        order.product = product_dict
        order.is_abandoned = False
        order.show_phone_number = order.show_phone_number or bool(product.store.plan)
        order.product_quantity=quantity
        order.created_at = timezone.now()
        order.save()

        # after order is confirmed
        send_new_order_notification(product.store, order)
        try:
            gs_info = order.store.gs_info
            phone_number = order.phone_number if order.store.plan else '/'
            order_data =[
                # order.id,
                order.created_at.strftime('%Y-%m-%d %H:%M'),
                order.product['title'],
                order.full_name,
                phone_number,
                order.shipping_state.name if order.shipping_state else _('No state'),
                (order.shipping_city.name if order.shipping_to_home else _('Office')) if order.shipping_city else '/',
                order.product_quantity,
                order.product['price'] or 0,
                order.product['shipping_cost'] or 0,
                order.product['total_price'],
                order.client_note,
            ]

            combination = order.product.get('combination')
            combination_text = ''
            if combination:
                for key, value in combination.items():
                    combination_text = f'{combination_text} {key}: {value},'
                combination_text = combination_text[:-1]
            order_data.append(combination_text)
            
            spreadsheet_id = gs_info.spreadsheet_id  # Assuming each seller has a `spreadsheet_id` field
            sheet_name = gs_info.sheet_name   # The name of the sheet/tab in the Google Sheet
            append_order_to_sheet(order_data, spreadsheet_id, sheet_name)
        except:
            pass  

        for conversions_api in order.store.conversions_apis.all():
            try: 
                FACEBOOK_PIXEL_ID = conversions_api.fb_pixel.pixel_id
                FACEBOOK_ACCESS_TOKEN = conversions_api.token
                test_event_code = conversions_api.test_event_code
                if FACEBOOK_ACCESS_TOKEN :
                    event_data={
                        'phone' : order.phone_number,
                        'first_name' : data.get('first_name'),
                        'last_name' : data.get('last_name'),
                        'city': order.shipping_city.name,
                        'state': order.shipping_state.name,
                        'country': 'DZ',
                        'client_ip_address': ip_address,
                        'custom_data': {
                            "currency" : 'DZD',
                            'value' : total_price,
                            "order_id": order_id,
                            "num_items": quantity,
                            "content_type": 'product', # or product_group 
                        }
                    }
                    respone = send_event_to_facebook(
                        FACEBOOK_ACCESS_TOKEN=FACEBOOK_ACCESS_TOKEN,
                        FACEBOOK_PIXEL_ID=FACEBOOK_PIXEL_ID,
                        event_data=event_data,
                        event_name='Purchase',
                        test_event_code = test_event_code
                    )
            except:
                pass
    

            
    except Exception as e:
        pass

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
    if len(phone_number) == 0 or (not phone_number.isdigit()):
        return JsonResponse({"detail": _('Phone number is invalid')}, status=400)
    product_id = data.get('product_id')
    state_id = data.get('state_id')
    full_name=data.get('full_name')
    address= data.get('shipping_address')
    price = data.get('price') or 0
    quantity = data.get('quantity') or 1
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
    if phone_number != 'locked' and (len(phone_number) == 0 or (not phone_number.isdigit())):
        return JsonResponse({"detail": _('Phone number is invalid')}, status=400)
    product_id = data.get('product_id')
    state_id = data.get('state_id')
    full_name=data.get('full_name')
    address= data.get('shipping_address')
    price = data.get('price') or 0
    quantity = data.get('quantity') or 1
    shipping_cost = data.get('shipping_cost')
    shipping_to_home= data.get('shipping_to_home')
    city_id = data.get('city_id')
    variants = data.get('variants')
    title = data.get('title')
    image = data.get('image')
    store_id = data.get('store_id')
    client_note= data.get('client_note')
    seller_note= data.get('seller_note')

    state = State.objects.get(id = state_id) if state_id else None
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
    order.shipping_city = City.objects.get(state=state, id = city_id) if city_id else None
    order.shipping_address = address
    order.full_name = full_name
    if order.show_phone_number:
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
        if store.credit < 10:
            return JsonResponse({
                    'phone_number': None,
                    'revelied': False,
                    'store_credit': store.credit
                })
        store.credit -= 10
        store.save()
        order.show_phone_number = True
        order.save()

    return JsonResponse({
        'phone_number': order.phone_number,
        'revelied': True,
        'store_credit': store.credit
    })
   
