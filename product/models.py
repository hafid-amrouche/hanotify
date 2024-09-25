from django.db import models
from category.models import Category
from django.contrib.auth.models import User 
from others.models import State
from store.models import Store


# Create your models here.

class Product(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    store= models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products', null=True, blank=True) # remove blank
    title = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=100, null=True, blank=True)
    mini_description = models.TextField(max_length=1000, null=True, blank=True)
    price = models.PositiveIntegerField(null=True, blank=True)
    original_price = models.PositiveIntegerField(null=True, blank=True)
    discount = models.TextField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=False)
    gallery_images = models.TextField(null=True, blank=True)
    image = models.TextField(null=True, blank=True)
    rich_text = models.TextField(null=True, blank=True)
    all_products_related = models.BooleanField(default=False)
    selected_categories= models.ManyToManyField(Category, related_name='products', blank=True)
    variants = models.JSONField(null=True, blank=True)
    ask_for_address=models.BooleanField(default=False)
    sku = models.CharField(max_length=50, null=True, blank=True)
    active = models.BooleanField(default=True)
    has_variants = models.BooleanField(default=False)
    max_index = models.PositiveIntegerField(default=1)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    # specs = models.JSONField(null=True, blank=True)
    # brand = models.CharField(max_length=50, null=True, blank=True)
    views = models.PositiveIntegerField(default=0)   
    # barcode = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

class VariantsCombination(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants_combinations')
    index = models.PositiveIntegerField()
    combination=models.JSONField(null=True, blank=True)
    image = models.TextField(null=True, blank=True)
    price = models.PositiveIntegerField(null=True, blank=True)
    original_price = models.PositiveIntegerField(null=True, blank=True)


class RelatedProduct(models.Model):
    main_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='related_products')
    related_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='products_related_to')
    order = models.PositiveIntegerField(null=True, blank=True)

class StateShippingCost(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='states_shipping_cost')
    cost =  models.PositiveIntegerField(blank=True, null=True)
    cost_to_home =  models.PositiveIntegerField(blank=True, null=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

