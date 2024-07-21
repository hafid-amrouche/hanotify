from django.db import models
from others.models import Image, SEO

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=50)
    icon = models.OneToOneField(Image, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(null=True, blank=True, max_length=1000)
    slug = models.SlugField(null=True, blank=True)
    seo = models.OneToOneField(SEO, null=True, blank=True, on_delete=models.SET_NULL)

