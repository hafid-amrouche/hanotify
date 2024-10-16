from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.http import JsonResponse
import json
from django.utils.translation import gettext as _
from .models import Visitor, Store, IpAddress, GSInfo, FBPixel, ConversionsApi, TikTokPixel
from django.utils import timezone
from functions import generate_token_from_id, get_client_ip
from product.serialiers import ProductSerializerA

from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings
from contants import media_files_domain
import requests
from django.core.paginator import Paginator, EmptyPage
from .models import HomePageSection
from category.models import Category
from product.models import Product
from django.db.models import F
from .serializers import StateCostSerializer
from .constants import default_home_page_section



        
# Create your views here.

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_shipping_costs(request):
    data = json.loads(request.body)
    costs_list = data.get('costs_list')
    store_id = data.get('store_id')
    store = request.user.stores.get(id=store_id)
   
    shipping_costs = store.shipping_costs.all()
    new_shipping_costs = []
    for cost in costs_list:
        costObj = shipping_costs.get(state_id=cost['id'])           
        costObj.cost = cost['cost']
        costObj.cost_to_home = cost['costToHome']
        costObj.save()
        if cost['cost'] or cost['costToHome']:
            new_shipping_costs.append(cost)
    
    receiver_url = media_files_domain + '/update-store-shipping-costs'
    response = requests.post(receiver_url,{
        'data': json.dumps({
            'MESSAGING_KEY': settings.MESSAGING_KEY,
            'costs_list': new_shipping_costs,
            'store_id': store_id
        })
    })
    if not response.ok:
        return JsonResponse({'detail': 'Error setting up your shipping costs'}, status=400)
        
    return JsonResponse({'detail': 'Success'}, status=200)

@api_view(['POST'])
def check_visitor(request):
    data = json.loads(request.body)
    tracker = data.get('tracker')
    store_id = data.get('id')
    store = Store.objects.get(domain__domain = store_id)
    ip_address = get_client_ip(request)
    if tracker:
        try:
            visitor = Visitor.objects.get(tracker = tracker, store = store)
        except:
            visitor = Visitor.objects.create(
                store = store, 
                last_visit = timezone.now()
            )
            visitor.tracker = generate_token_from_id(visitor.id)

        IpAddress.objects.get_or_create(
            ip_address = ip_address,
            visitor = visitor
        )
        visitor.last_visit =timezone.now()
        visitor.save()
        return JsonResponse({
            'tracker': visitor.tracker,
            'isBlocked': visitor.blocked
        })
    else:
        ip_addresses = IpAddress.objects.filter(ip_address=ip_address, visitor__store = store)
        
        if ip_addresses.exists():
            blocked_addresses = ip_addresses.filter(visitor__blocked = True)
            if blocked_addresses.exists(): 
                visitor = blocked_addresses.last().visitor
                visitor.last_visit =timezone.now()
                visitor.save()
                return JsonResponse({
                    'tracker': visitor.tracker,
                    'isBlocked': True
                })

            else:
                visitor = ip_addresses.last().visitor
                visitor.last_visit =timezone.now()
                visitor.save()
                return JsonResponse({
                    'tracker': visitor.tracker,
                    'isBlocked': False
                })
        else:
            visitor = Visitor.objects.create(
                store = store, 
                last_visit = timezone.now()
            )
            visitor.tracker = generate_token_from_id(visitor.id)
            visitor.save()
            IpAddress.objects.get_or_create(
                ip_address = ip_address,
                visitor = visitor
            )
            return JsonResponse({
                'tracker': visitor.tracker,
                'isBlocked': False
            })

@api_view(['POST'])
def block_visitor(request):
    data = json.loads(request.body)
    id = data.get('id')
    store = request.user.stores.get(id = data.get('store_id'))
    visitor = store.visitors.get(id = id)
    visitor.blocked = True
    visitor.save()
    return JsonResponse({
        'blocked': True
    })

@api_view(['POST'])
def unblock_visitor(request):
    data = json.loads(request.body)
    id = data.get('id')
    store = request.user.stores.get(id = data.get('store_id'))
    visitor = store.visitors.get(id = id)
    visitor.blocked = False
    visitor.save()
    return JsonResponse({
        'blocked': False
    })

def get_google_sheets_service():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = settings.BASE_DIR / 'json_files/service_account.json'
    
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    service = build('sheets', 'v4', credentials=credentials)
    return service

def check_sheet_validity(spreadsheet_id, sheet_name):
    service = get_google_sheets_service()
    
    try:
        # Get the spreadsheet details
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        
        # Get the list of sheets
        sheets = spreadsheet.get('sheets', [])
        
        # Check if the sheet_name exists
        for sheet in sheets:
            if sheet.get('properties', {}).get('title') == sheet_name:
                return True  # Valid sheet found
        
        return False  # Sheet name not found
    
    except Exception as e:
        print(f"Error: {e}")
        return False  # Spreadsheet ID not found or other error

def check_and_set_initial_data(spreadsheet_id, sheet_name, initial_data):
    service = get_google_sheets_service()

    # Check if A1 is empty
    range_name = f"{sheet_name}!A1"
    
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()

        values = result.get('values', [])

        # If the sheet is empty (A1 is empty)
        if not values:
            # Set the initial data in A1
            body = {
                'values': [initial_data]  # initial_data should be a list representing the row
            }
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                body=body
            ).execute()
            print("The sheet was empty. Data has been added to A1.")
        else:
            print("The sheet is not empty. No changes made.")
        
        return True

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

initial_data = [
    _('Date'),
    _('Title'),
    _('Full name'),
    _('Phone number'),
    _('State'),
    _('City'),
    _('Quantity'),
    _('Price'),
    _('Shipping cost'),
    _('Total price'),
    _('Note'),
    _('Variants'),
] 

@api_view(['POST'])
def set_up_google_sheets(request):
    data = json.loads(request.body)
    store = request.user.stores.get(id = data.get('store_id'))
    spreadsheet_id = data.get('spreadsheet_id')
    sheet_name = data.get('sheet_name')
    is_valid = check_and_set_initial_data(spreadsheet_id, sheet_name, initial_data)
    if is_valid:
        [gs_info, created] = GSInfo.objects.get_or_create(store=store)
        gs_info.spreadsheet_id = spreadsheet_id
        gs_info.sheet_name = sheet_name
        gs_info.save()
        return JsonResponse({'detail': 'Your google sheets is connected successfully.'})
    else:
        return JsonResponse({'detail': 'Your google sheets is not connected, make sure your shared your google sheet with the email we provided.'}, status=400)
    
@api_view(['GET'])
def get_gs_info(request):
    data = request.GET
    store = request.user.stores.get(id = data.get('store_id'))
    try:
        gs_info = store.gs_info
        return JsonResponse(
            {'gsInfo': {
                'spreadsheetId': gs_info.spreadsheet_id,
                'sheetName': gs_info.sheet_name
            }}
        )
    except:
        return JsonResponse({
            'gsInfo': None
        })
    
@api_view(['POST'])
def delete_gs_info(request):
    
    data = json.loads(request.body)
    store = request.user.stores.get(id = data.get('store_id'))
    try:
        store.gs_info.delete()
    except:
        pass
    return JsonResponse(
            {'detail': 'Deleted'}
        )

def update_fb_pixel(fb_pixels, store_id):
    receiver_url = media_files_domain + '/update-fb-pixel'
    response = requests.post(receiver_url,{
        'store_id': store_id,
        'fb_pixels' :  fb_pixels,
        'MESSAGING_KEY': settings.MESSAGING_KEY
    })
    if not response.ok:
        return JsonResponse({'detail': 'Error setting up your facebook pixel'}, status=400)

@api_view(['POST'])
def set_up_fb_pixel(request):
    data = json.loads(request.body)
    store_id = data.get('store_id')
    store = request.user.stores.get(id = store_id)
    pixel_id = data.get('pixel_id')
    if not pixel_id or (FBPixel.objects.filter(store=store, pixel_id=pixel_id).exists()):
        return JsonResponse({'detail': 'This facebook pixel id already exists'}, status=400)
    new_list = list(store.fb_pixels.values_list('pixel_id', flat=True))
    new_list.append(pixel_id)
    update_fb_pixel(new_list, store.id)
    FBPixel.objects.create(store=store, pixel_id=pixel_id)
    return JsonResponse({'detail': 'Your facebook pixel is connected successfully.'})
    

@api_view(['GET'])
def get_fb_pxel(request):
    data = request.GET
    store = request.user.stores.get(id = data.get('store_id'))
    fb_pixels = store.fb_pixels.all()
    return JsonResponse(
        [ {
            'fbPixel': fb_pixel.pixel_id,
            'apiToken': fb_pixel.conversions_api.token if fb_pixel.conversions_api else None,
            'eventTestCode': fb_pixel.conversions_api.test_event_code if fb_pixel.conversions_api else None,
        } for fb_pixel in fb_pixels],
        safe=False
    )
    
@api_view(['POST'])
def delete_fb_pixel(request):
    
    data = json.loads(request.body)
    store_id = data.get('store_id')
    pixel_id = data.get('pixel_id')
    store = request.user.stores.get(id=store_id)
    store_fb_pixels = FBPixel.objects.filter(store = store)
    pixel = store_fb_pixels.get(pixel_id=pixel_id)
    
    new_list = list(store_fb_pixels.values_list('pixel_id', flat=True))
    new_list.remove(pixel_id)

    update_fb_pixel(new_list, store.id)
    try:
        pixel.delete()
        pixel.conversions_api.delete()
    except:
        pass
    return JsonResponse(
            {'detail': 'Deleted'}
        )

@api_view(['POST'])
def set_up_conversion_api_token(request):
    data = json.loads(request.body)
    store_id = data.get('store_id')
    store = request.user.stores.get(id = store_id)
    conversion_api_access_token = data.get('conversion_api_access_token')
    pixel_id = data.get('pixel_id')
    fb_pixel = FBPixel.objects.get(store=store, pixel_id=pixel_id)
    if conversion_api_access_token:
        conversions_api = ConversionsApi.objects.create(
            store = store,
            token = conversion_api_access_token,
        )
        fb_pixel.conversions_api = conversions_api
        fb_pixel.save()
    else:
        return JsonResponse({'detail': 'Error while setting your conversions api'}, status=400)
    return JsonResponse({'detail': 'Meta api conversions token is connected successfully.'})
    
@api_view(['POST'])
def delete_conversion_api_token(request):
    data = json.loads(request.body)
    store_id = data.get('store_id')
    store = request.user.stores.get(id=store_id)
    pixel_id = data.get('pixel_id')
    fb_pixel = FBPixel.objects.get(store=store, pixel_id=pixel_id)
    try:
        fb_pixel.conversions_api.delete()
    except:
        pass
    return JsonResponse(
            {'detail': 'Deleted'}
        )

@api_view(['POST'])
def set_up_test_code_event(request):
    data = json.loads(request.body)
    store_id = data.get('store_id')
    pixel_id = data.get('pixel_id')
    store = request.user.stores.get(id = store_id)
    test_event_code = data.get('test_event_code')
    fb_pixel = FBPixel.objects.get(store=store, pixel_id=pixel_id)
    conversions_api = fb_pixel.conversions_api
    conversions_api.test_event_code = test_event_code or None
    conversions_api.save()
    return JsonResponse({'detail': 'Success'})

@api_view(['POST'])
def set_up_tiktok_pixel(request):
    data = json.loads(request.body)
    store_id = data.get('store_id')
    store = request.user.stores.get(id = store_id)
    pixel_id = data.get('pixel_id').strip()
    if not pixel_id or (TikTokPixel.objects.filter(store=store, pixel_id=pixel_id).exists()):
        return JsonResponse({'detail': 'pixel id already exists'}, status=400)
    receiver_url = media_files_domain + '/update-tiktok-pixels'
    old_pixels_id = list(store.tiktok_pixels.values_list('pixel_id', flat=True))
    old_pixels_id.append(pixel_id)
    response = requests.post(receiver_url,{
        'store_id': store.id,
        'pixels_id' :  old_pixels_id,
        'MESSAGING_KEY': settings.MESSAGING_KEY
    })
    if not response.ok:
        raise

    tiktok_pixel = TikTokPixel.objects.create(store=store)
    tiktok_pixel.pixel_id = pixel_id
    tiktok_pixel.save()
    return JsonResponse({'detail': 'Your tiktok pixel is connected successfully.'})
    
@api_view(['GET'])
def get_tiktok_pixels(request):
    data = request.GET
    store = request.user.stores.get(id = data.get('store_id'))
    try:
        return JsonResponse(
            {
                'tiktokPixels': list(store.tiktok_pixels.values_list('pixel_id', flat=True)),
            }
        )
    except:
        return JsonResponse({
            'tiktokPixels': None
        })
    
@api_view(['POST'])
def delete_tiktok_pixel(request):
    data = json.loads(request.body)
    store_id = data.get('store_id')
    pixel_id = data.get('pixel_id')
    store = request.user.stores.get(id=store_id)
    tiktok_pixel = TikTokPixel.objects.get(store=store, pixel_id=pixel_id)
    receiver_url = media_files_domain + '/update-tiktok-pixels'

    new_list = list(store.tiktok_pixels.values_list('pixel_id', flat=True))
    new_list.remove(pixel_id)
    requests.post(receiver_url,{
        'store_id': store.id,
        'pixels_id': new_list,
        'MESSAGING_KEY': settings.MESSAGING_KEY
    })
    try:
        tiktok_pixel.delete()
    except:
        pass
    return JsonResponse(
            {'detail': 'Deleted'}
        )

@api_view(['POST'])
def update_store_info(request):
    data = json.loads(request.body)
    store_id = data.get('store_id')
    store = request.user.stores.get(id=store_id)

    logo = data.get('logo')
    color_primary = data.get('primary_color')
    color_primary_dark = data.get('primary_color_dark') 
    borders_rounded = data.get('borders_rounded')
    name = data.get('name')
    description = data.get('description')
    favicon = data.get('favicon', '')
    header_outlined = data.get('header_outlined')
    language = data.get('language')
    mode = data.get('mode')
    footer = data.get('footer')
    images_urls = data.get('images_urls')

    store.logo = logo
    store.color_primary = color_primary
    store.color_primary_dark = color_primary_dark
    store.borders_rounded = borders_rounded
    store.name=name
    store.description =description
    store.favicon =favicon
    store.header_outlined = header_outlined
    store.language = language
    store.mode = mode
    store.footer = footer


    store_dict = {
        'primaryColor': color_primary,
        'primaryColorDark': color_primary_dark,
        'bordersRounded': borders_rounded,
        'logo' :  logo,
        'name': name,
        'description': description,
        'favicon': favicon,
        'headerOutlined': header_outlined,
        'language': language,
        'mode': mode,
        'footer': footer
    }
    receiver_url = media_files_domain + '/save-store'
    response = requests.post(receiver_url,{
        'id': store.id,
        'MESSAGING_KEY': settings.MESSAGING_KEY,
        'store': json.dumps(store_dict),
        'images_urls' : images_urls
    })
    if not response.ok:
        raise
    store.save()
    return JsonResponse({'detail': 'success'})
    
@api_view(['POST'])
def non_selected_products_container_products(request):
    data = json.loads(request.body)
    domain = data.get('domain')    

    store = Store.objects.get(owner = request.user,domain__domain=domain)
    if not store.active:
        return JsonResponse({'detail', _('Store not found')}, status=400)
    
    excluded_products = data.get('excluded_products')    
    top_picks = store.products.filter(active=True, is_available=True).exclude(id__in = excluded_products)

    page = data.get('page')
    
    paginator = Paginator(top_picks, 3)
    try:
        products = paginator.page(page)  # Get products for the desired page
    except EmptyPage:
        products = paginator.page(paginator.num_pages)  # If page is out of range, deliver last page of results.

    return Response({
        'products': ProductSerializerA(products, many=True).data,    
        'numPages': paginator.num_pages,
        'hasNext': products.has_next(),
        'hasPrev': products.has_previous(),    
    })

@api_view(['POST'])
def non_selected_category_products(request):
    data = json.loads(request.body)
    domain = data.get('domain')    
    category_id = data.get('category_id') 

    store = Store.objects.get(owner = request.user,domain__domain=domain)
    category = store.categories.get(id=category_id)
    if not store.active:
        return JsonResponse({'detail', _('Store not found')}, status=400)
    
    excluded_products = data.get('excluded_products')    
    category_products = category.products.filter(active=True, is_available=True).exclude(id__in = excluded_products)
    page = data.get('page')
    
    paginator = Paginator(category_products, 12)
    try:
        products = paginator.page(page)  # Get products for the desired page
    except EmptyPage:
        products = paginator.page(paginator.num_pages)  # If page is out of range, deliver last page of results

    return Response({
        'products': ProductSerializerA(products, many=True).data,    
        'numPages': paginator.num_pages,
        'hasNext': products.has_next(),
        'hasPrev': products.has_previous(),    
    })

@api_view(['POST'])
def update_homepage(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Load the JSON payload
            
            # Get the home page for the store (assuming store_id is in the request or data)
            store_id = data.get('store_id')
            store = request.user.stores.get(id= store_id)
            home_page = store.home_page
            images = data.get('images')

            receiver_url = media_files_domain + '/save-store-images'
            response = requests.post(receiver_url, {
                'data': json.dumps({
                    'store_id': store.id,
                    'MESSAGING_KEY': settings.MESSAGING_KEY,
                    'images_urls' : images
                })
            })

            if not response.ok:
                return JsonResponse({'detail': 'file server error'}, status=500)
            # Iterate through the sections in the data
            to_saved_id = []
            order = 1
            for section_data in data['sections']:
                section_id = section_data.get('id')
                section, created = HomePageSection.objects.update_or_create(
                    home_page=home_page,
                    section_id=section_id,
                )
                to_saved_id.append(section.id)
                category = None
                section_type = section_data.get('type')
                if section_type == 'products-container':  # Assuming it's a category if it's an integer
                    section.products.clear()
                    for product_data in section_data.get('products', []):
                        product_id = product_data['product_id']
                        product = Product.objects.get(id=product_id)
                        section.products.add(product)
                    
                    section.active = True

                elif section_type == 'category':  # Assuming it's a category if it's an integer
                    category_id = section_data.get('id').split('-')[1]
                    try:
                        category = Category.objects.get(id=category_id)
                    except:
                        pass
                    section.products.clear()
                    for product_data in section_data.get('products', []):
                        product_id = product_data['product_id']
                        product = Product.objects.get(id=product_id)
                        section.products.add(product)

                    section.active = section_data.get('active')

                elif section_type == 'swiper':
                    
                    section.image_objects = section_data.get('imageObjects')
                    section.active = True

                section.title = section_data.get('title')
                section.device = section_data.get('device')
                section.category = category 
                section.section_id = section_id
                section.type = section_type
                section.design = section_data.get('design')
                section.order = order
                order += 1
                section.save()

            home_page.sections.exclude(id__in=to_saved_id).exclude(type='category').delete()
            home_page.general_design = data['general_design']
            home_page.save()
            return JsonResponse({'status': 'success', 'message': 'Home page sections populated successfully.'}, status=201)
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

def serialized_category_preview_products(query):
    return list(
        query.annotate(
            product_id = F('id'),
        ).values('product_id','image', 'price', 'title', 'original_price', 'slug'))

def home_page_section_serializer(home_page_sections):
        def serialize_section(section):
            if section.type == 'products-container':
                return {
                        "id": section.section_id,
                        "title": section.title,
                        "products": serialized_category_preview_products(section.products),
                        "type": "products-container",
                        "active": True,
                        "design": section.design,
                        "device": section.device
                    }
        
            if section.type == 'category':
                return {
                        "id": section.section_id,
                        "title": section.category.label,
                        "products": serialized_category_preview_products(section.products),
                        "type": "category",
                        "active": section.active,
                        "design": section.design,
                        "device": section.device
                    }
            
            if section.type == 'swiper':
                return {
                    "id": section.section_id,
                    "title": section.title,
                    "imageObjects": section.image_objects,
                    "type": "swiper",
                    "active": True,
                    "design": section.design,
                    "device": section.device
                }
        return [
            serialize_section(section) 
            for section in home_page_sections
        ]

@api_view(['GET'])
def home_customization_products(request):
    domain = request.GET.get('domain')    

    store = Store.objects.get(domain__domain=domain)
    if not store.active:
        return JsonResponse({'detail', _('Store not found')}, status=400)
    
    home_page = store.home_page
    if(home_page.auto):
        return Response({
            'sections': home_page_section_serializer([default_home_page_section(store.products.filter(active=True, is_available=True)[:20])]),
            'store': {
                'primaryColor': store.color_primary,
                'primaryColorDark': store.color_primary_dark,
                'visionMode': store.mode,
                'bordersRounded': store.borders_rounded
            },
            'generalDesign':  home_page.general_design,
            'home_page_mode' : home_page.auto
        })
    else:
        return Response({
            'sections': home_page_section_serializer(home_page.sections.order_by('order')),
            'store': {
                'primaryColor': store.color_primary,
                'primaryColorDark': store.color_primary_dark,
                'visionMode': store.mode,
                'bordersRounded': store.borders_rounded
            },
            'generalDesign':  home_page.general_design,
            'home_page_mode' : home_page.auto
        })




@api_view(['POST'])
def toggle_auto_home_page(request):
    data = json.loads(request.body)
    store_id = data.get('store_id')
    store = request.user.stores.get(id=store_id)
    store.home_page.auto = not store.home_page.auto
    store.home_page.save()
    return JsonResponse({
        'home_page_mode': store.home_page.auto,
        'sections': home_page_section_serializer([default_home_page_section(store.products.all()[:20])]) if store.home_page.auto else home_page_section_serializer(store.home_page.sections.order_by('order'))
    })
# hanotify.store

@api_view(['GET'])
def store_home_page_sections(request):
    domain = request.GET.get('domain')    

    store = Store.objects.get(domain__domain=domain)
    if not store.active:
        return JsonResponse({'detail', _('Store not found')}, status=400)
    
    home_page = store.home_page
    if(home_page.auto):
        return Response({
            'sections': home_page_section_serializer([default_home_page_section(store.products.filter(active=True, is_available=True)[:20])]),
            'store': {
                'primaryColor': store.color_primary,
                'primaryColorDark': store.color_primary_dark,
                'visionMode': store.mode,
                'bordersRounded': store.borders_rounded
            },
            'generalDesign':  home_page.general_design,
            'home_page_mode' : home_page.auto
        })
    else:
        return Response({
            'sections': home_page_section_serializer(home_page.sections.filter(active=True).order_by('order')),
            'store': {
                'primaryColor': store.color_primary,
                'primaryColorDark': store.color_primary_dark,
                'visionMode': store.mode,
                'bordersRounded': store.borders_rounded
            },
            'generalDesign':  home_page.general_design,
            'home_page_mode' : home_page.auto
        })


@api_view(['GET'])
def sidebar_content(request):
    domain = request.GET.get('domain')    

    store = Store.objects.get(domain__domain=domain)
    if not store.active:
        return JsonResponse({'detail', _('Store not found')}, status=400)
    
    catgeories_list = [
        {
            'name' : category.label,
            'slug': category.slug
        }
        for category in store.categories.filter(home_page_section__active=True)
    ]
    catgeories_list.insert(0, {
        'name': 'Top picks',
        'slug': 'top-picks'
    })
    return JsonResponse({
        'categories': catgeories_list
    })

@api_view(['GET'])
def home_page_sections(request):
    # domain = request.GET.get('domain')    

    # store = Store.objects.get(domain__domain=domain)
    # if not store.active:
    #     return JsonResponse({'detail', _('Store not found')}, status=400)
    
    # home_page = store.home_page
    # return Response({
    #     'sections': home_page_section_serializer(home_page.sections.filter(active=True).order_by('order')),
    #     'store': {
    #         'primaryColor': store.color_primary,
    #         'primaryColorDark': store.color_primary_dark,
    #         'visionMode': store.mode,
    #         'bordersRounded': store.borders_rounded
    #     },
    #     'generalDesign':  home_page.general_design,
    # })
    pass

@api_view(['GET'])
def get_store_credit(request):
    store_id = request.GET.get('store_id')
    store = Store.objects.get(id=store_id, owner=request.user)
    
    return JsonResponse({
        'credit' : store.credit    
    })

@api_view(['GET'])
def get_default_shipping_cost(request):
    store_id = request.GET.get('store_id')
    store = request.user.stores.get(id = store_id)
    return Response(StateCostSerializer(store.shipping_costs.all(), many=True).data)

