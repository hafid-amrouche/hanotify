from django.db.models.signals import post_save
from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings
from django.utils.translation import gettext as _

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Order
from .serializers import OrderPreviewSerializer

def send_new_order_notification(instance):
        channel_layer = get_channel_layer()

        # Send message to the orders group
        async_to_sync(channel_layer.group_send)(
            "orders",
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

def post_create(sender, instance, created,  **kwargs):
    order = instance
    if created:
        order.status = order.store.statuses.first()
        order.save()
    if not order.is_abandoned:
        send_new_order_notification(instance)
        try:
            gs_info = order.store.gs_info
            order_data =[
                order.id,
                order.full_name,
                order.product['title'],
                order.created_at.strftime('%Y-%m-%d %H:%M'),
                order.phone_number,
                order.shipping_state.name if order.shipping_state else _('No state'),
                (order.shipping_city.name if order.shipping_to_home else _('Office')) if order.shipping_city else '/',
                order.product_quantity,
                order.product['shipping_cost'] or 0,
                order.product['total_price'],
            ]

            combination = order.product.get('combination')
            if combination:
                combination_text = ''
                for key, value in combination.items():
                    combination_text = f'{combination_text} {key}: {value},'
                combination_text = combination_text[:-1]
                order_data.append(combination_text)

            spreadsheet_id = gs_info.spreadsheet_id  # Assuming each seller has a `spreadsheet_id` field
            sheet_name = gs_info.sheet_name   # The name of the sheet/tab in the Google Sheet
            append_order_to_sheet(order_data, spreadsheet_id, sheet_name)
        except:
            pass       

post_save.connect(post_create, Order)