from django.db import models
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

        