from django.db import models
from product.models import Product
from others.models import State, City
from django.contrib.auth.models import User 

# Create your models here.

class Order(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=50, null=True, blank=True)
    phone_number = models.CharField(max_length=13, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)
    address = models.TextField(max_length=500, null=True, blank=True)
    quantity = models.SmallIntegerField()
    home_delevery = models.BooleanField(null=True, blank=True)
    is_abandoned = models.BooleanField(default=True)
    status = models.CharField(choices=(
        ('confirmed', 'Confirmed'),
        ('did_not_answer_phone', 'DidNotAnswerPhone'),
        ('postponed', 'Postponed'),
        ('canceled', 'Canceled'),
        ('canceled_from_client', 'CanceledFromClient'),
        ('waiting_for_client_call', 'WaitingForClientCall'),
        ('client_out_of_service', 'ClientOutOfService'),
        ('at_delevery_company', 'AtDeleveryCompany'),
        ('completed', 'Completed'),

    ), max_length=50)

    class Meta:
        ordering = ['-created_at']  # Default ordering: newest orders first
