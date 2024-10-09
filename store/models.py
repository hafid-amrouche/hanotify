from django.db import models
from django.contrib.auth.models import User 
from others.models import State
# Create your models here.

class Store(models.Model):
    owner= models.ForeignKey(User, on_delete=models.CASCADE, related_name='stores')
    active = models.BooleanField(default=True)
    # Store design
    logo= models.TextField(null=True, blank=True)
    favicon= models.TextField(null=True, blank=True)
    color_primary=models.CharField(max_length=7, default='#446ec3')
    color_primary_dark=models.CharField(max_length=7, default='#446ec3')
    header_outlined=models.BooleanField(default=False)
    borders_rounded=models.BooleanField(default=True)
    name=models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)    
    language = models.CharField(max_length=2, default='ar')
    mode = models.CharField(max_length=10, default='light')
    has_custom_domain = models.BooleanField(default=False)
    policies = models.JSONField(blank=True, null=True)
    phone_numbers = models.JSONField(blank=True, null=True)
    facebook = models.TextField(blank=True, null=True)
    instagram = models.TextField(blank=True, null=True)
    youtube = models.TextField(blank=True, null=True)
    ask_for_client_note = models.BooleanField(default=True)
    footer = models.TextField(default='')    
    credit = models.BigIntegerField(default=300)
    plan = models.CharField(max_length=10, null=True, blank=True)


class HomePage(models.Model):
    store = models.OneToOneField(Store, on_delete=models.CASCADE, related_name='home_page')
    general_design = models.JSONField(null=True, blank=True)





class HomePageSection(models.Model):
    home_page = models.ForeignKey(HomePage, on_delete=models.CASCADE, related_name='sections')   
    section_id = models.CharField(max_length=50)
    type = models.CharField(max_length=50, null=True, blank=True)
    design = models.JSONField(null=True, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    # products container only
    active = models.BooleanField(default=False)
    category = models.OneToOneField('category.category', on_delete= models.CASCADE, null=True, blank=True, related_name='home_page_section')
    products = models.ManyToManyField('product.product')

    # swiper container only    
    title = models.CharField(max_length=50, null=True, blank=True)
    image_objects = models.JSONField(null=True, blank=True)
    device = models.CharField(max_length=50, null=True, blank=True)


class Domain(models.Model):
    domain = models.CharField(max_length=255, unique=True)
    store = models.OneToOneField(Store, on_delete=models.CASCADE, related_name='domain')

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
    
class ConversionsApi(models.Model):
    store=models.ForeignKey(Store, on_delete=models.CASCADE, related_name='conversions_apis', null=True, blank=True)
    token = models.TextField(max_length=400, null=True, blank=True)
    test_event_code = models.CharField(max_length=20, null=True, blank=True)

class FBPixel(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='fb_pixels')
    pixel_id = models.CharField(max_length=20)
    conversions_api = models.OneToOneField(ConversionsApi, on_delete=models.SET_NULL, related_name='fb_pixel', null=True, blank=True)


class TikTokPixel(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='tiktok_pixels')
    pixel_id = models.CharField(max_length=255)

class VIPStore(models.Model):
    store = models.OneToOneField(Store, on_delete=models.CASCADE, related_name='vip_store')

class StoreTopPick(models.Model):
    store =  models.ForeignKey(Store, on_delete=models.CASCADE, related_name='top_picks')
    product = models.ForeignKey('product.product', on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField()