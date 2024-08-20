from django.db import models
from others.models import Image, SEO
from django.contrib.auth.models import User 
from store.models import Store


# Create your models here.

class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='categories') # remove blank
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True, related_name='categories') # remove blank
    label = models.CharField(max_length=50)
    image = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True, max_length=1000)
    slug = models.SlugField(null=True, blank=True)
    class Meta:
        ordering = ['-id']  # Default ordering: newest orders first

