from django.db import models
from django.db.models.signals import post_save
from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings
from django.utils.translation import gettext as _

class Order(models.Model):
    store= models.ForeignKey('store.Store', on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    product =models.JSONField(null=True, blank=True)
    shipping_state = models.ForeignKey('others.State', on_delete=models.SET_NULL, null=True, blank=True)
    shipping_city = models.ForeignKey('others.City', on_delete=models.SET_NULL, null=True, blank=True)
    shipping_address = models.TextField(max_length=200, null=True, blank=True)
    full_name = models.CharField(max_length=50, null=True, blank=True)
    phone_number = models.CharField(max_length=13, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    shipping_to_home = models.BooleanField(default=False)
    is_abandoned = models.BooleanField(default=True)
    status = models.ForeignKey('store.Status', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    visitor = models.ForeignKey('store.Visitor', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    product_quantity = models.PositiveSmallIntegerField(default=1)
    made_by_seller = models.BooleanField(default=False)
    show_phone_number = models.BooleanField(default=False)
    seller_note = models.TextField(max_length=1000, null=True, blank=True)
    client_note = models.TextField(max_length=1000, null=True, blank=True)

    token = models.TextField(null=True, blank=True)
    class Meta:
        ordering = ['-id']  # Default ordering: newest orders first


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
        try:
            gs_info = order.store.gs_info
            order_data =[
                order.id,
                order.full_name,
                order.product['title'],
                order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                order.phone_number,
                order.shipping_state.name,
                order.shipping_city.name if order.shipping_to_home else _('Office'),
                order.status.text,
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