from django.db import models
from django.contrib.auth.models import User 
from others.models import Image, SEO, State
from others.models import Location
from orders.models import Order
# Create your models here.

class Store(models.Model):
    owner= models.ForeignKey(User, on_delete=models.CASCADE, related_name='stores')
    name=models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    domain = models.CharField(max_length=255, unique=True, null=True, blank=True)
    has_custom_domain = models.BooleanField(default=False)
    sub_domain = models.CharField(max_length=255, unique=True, null=True, blank=True)
    logo= models.ForeignKey(Image, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, blank=True, null=True)
    policies = models.JSONField(blank=True, null=True)
    phone_numbers = models.JSONField(blank=True, null=True)
    facebook = models.TextField(blank=True, null=True)
    instagram = models.TextField(blank=True, null=True)
    youtube = models.TextField(blank=True, null=True)

class IpAddress(models.Model):
    visitor = models.ForeignKey('store.Visitor', on_delete=models.CASCADE, related_name='ip_addresses')
    ip_address = models.TextField()

class Status(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='statuses')
    text = models.TextField(max_length=255)
    icon = models.TextField(null=True, blank=True)
    order = models.PositiveSmallIntegerField(null=True, blank=True)
    
class StoreOptions(models.Model):
    primary_color = models.CharField(max_length=7, default='#c8102e')


class StateShippingCost(models.Model):
    store= models.ForeignKey(Store, blank=True, null=True, on_delete=models.CASCADE, related_name='shipping_costs')
    cost =  models.PositiveIntegerField(blank=True, null=True)
    cost_to_home =  models.PositiveIntegerField(blank=True, null=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='store_shipping_costs')

class Visitor(models.Model):
    store=models.ForeignKey(Store, on_delete=models.CASCADE, related_name='visitors')
    tracker = models.TextField(null=True, blank=True)
    last_visit = models.DateTimeField(null=True, blank=True)
    blocked = models.BooleanField(default=False)

class GSInfo(models.Model):
    store = models.OneToOneField(Store, on_delete=models.CASCADE, related_name='gs_info')
    spreadsheet_id = models.CharField(max_length=220)
    sheet_name = models.CharField(max_length=220)