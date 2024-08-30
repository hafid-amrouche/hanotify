from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Image(models.Model):
    url = models.TextField()
    path = models.TextField()

class State(models.Model):
    code = models.CharField(max_length=2)
    name = models.CharField(max_length=50)
    name_ar = models.CharField(max_length=50)

class City(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities')
    name = models.CharField(max_length=50)
    name_ar = models.CharField(max_length=50)

class Location(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True)
    street = models.CharField(max_length=255)
    coordinates = models.JSONField(null=True, blank=True)

class SEO(models.Model):
    meta_slug = models.TextField(max_length=200, null=True, blank=True)
    meta_title= models.TextField(max_length=100, null=True, blank=True)
    meta_description=models.TextField(max_length=1000, null=True, blank=True)
    image = models.OneToOneField(Image, on_delete=models.SET_NULL, null=True, blank=True)