from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
import json
from django.utils.translation import gettext as _
from .models import Visitor, Store, IpAddress, GSInfo, FBPixel
from django.utils import timezone
from functions import generate_token_from_id, get_client_ip

from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings
from time import sleep
from contants import media_files_domain
import requests
        
# Create your views here.

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_shipping_costs(request):
    data = json.loads(request.body)
    costs_list = data.get('costs_list')
    store = request.user.stores.first()
    for cost in costs_list:
        costObj = store.shipping_costs.get(state_id=cost['id'])
        costObj.cost = cost['cost']
        costObj.cost_to_home = cost['costToHome']
        costObj.save()
    return JsonResponse({'detail': 'Success'}, status=200)

@api_view(['POST'])
def check_visitor(request):
    data = json.loads(request.body)
    tracker = data.get('tracker')
    store_id = data.get('id')
    store = Store.objects.get(domain = store_id)
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
    _('ID'),
    _('Full name'),
    _('Title'),
    _('Date'),
    _('Phone number'),
    _('State'),
    _('City'),
    _('Status'),
    _('Quantity'),
    _('Shipping cost'),
    _('Total price'),
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

def update_fb_pixel(fb_pixel, store_domain):
    receiver_url = media_files_domain + '/save-fb-pixel'
    response = requests.post(receiver_url,{
        'store_domain': store_domain,
        'fb_pixel' :  fb_pixel,
        'MESSAGING_KEY': settings.MESSAGING_KEY
    })
    if not response.ok:
        raise

@api_view(['POST'])
def set_up_fb_pixel(request):
    data = json.loads(request.body)
    store_id = data.get('store_id')
    store = request.user.stores.get(id = store_id)
    pixel_id = data.get('pixel_id')
    update_fb_pixel(pixel_id, store.domain)
    [fb_pixel, created] = FBPixel.objects.get_or_create(store=store)
    fb_pixel.pixel_id = pixel_id
    fb_pixel.save()
    return JsonResponse({'detail': 'Your facebook pixel is connected successfully.'})
    

@api_view(['GET'])
def get_fb_pxel(request):
    data = request.GET
    store = request.user.stores.get(id = data.get('store_id'))
    try:
        fb_pixel = store.fb_pixel
        return JsonResponse(
            {'fbPixel': fb_pixel.pixel_id}
        )
    except:
        return JsonResponse({
            'fbPixel': None
        })
    
@api_view(['POST'])
def delete_fb_pixel(request):
    
    data = json.loads(request.body)
    store_id = data.get('store_id')
    store = request.user.stores.get(id=store_id)
    receiver_url = media_files_domain + '/delete-fb-pixel'

    requests.post(receiver_url,{
        'store_domain': store.domain,
        'MESSAGING_KEY': settings.MESSAGING_KEY
    })
    try:
        store.fb_pixel.delete()
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
    primary_color = data.get('primary_color')
    borders_rounded = data.get('borders_rounded')
    name = data.get('name')
    description = data.get('description')

    store.logo = logo
    store.primary_color = primary_color
    store.borders_rounded = borders_rounded
    store.name=name
    store.description =description

    receiver_url = media_files_domain + '/save-store'

    store_dict = {
        'primaryColor': primary_color,
        'bordersRounded': borders_rounded,
        'logo' :  logo,
        'name': name,
        'description': description,
    }
    try:
        store_dict['facebookPixelId'] = store.fb_pixel.pixel_id
    except:
        pass
    response = requests.post(receiver_url,{
        'id': store.id,
        'MESSAGING_KEY': settings.MESSAGING_KEY,
        'store': json.dumps(store_dict)
    })
    if not response.ok:
        raise

    store.save()
    return JsonResponse({'detail': 'success'})
    