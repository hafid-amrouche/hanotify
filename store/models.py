from django.db import models
from django.contrib.auth.models import User 
from others.models import Image, SEO
from others.models import Location

# Create your models here.

class Store(models.Model):
    owner= models.ForeignKey(User, on_delete=models.CASCADE, related_name='stores')
    name=models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    domain = models.CharField(max_length=255, unique=True, null=True, blank=True)
    logo= models.ForeignKey(Image, on_delete=models.SET_NULL, null=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, blank=True, null=True)
    policies = models.JSONField(blank=True, null=True)
    phone_numbers = models.JSONField()
    facebook = models.TextField(blank=True, null=True)
    instagram = models.TextField(blank=True, null=True)
    youtube = models.TextField(blank=True, null=True)
    seo = models.OneToOneField(SEO, null=True, blank=True, on_delete=models.SET_NULL)

class StoreOptions(models.Model):
    primary_color = models.CharField(max_length=7, default='#c8102e')

