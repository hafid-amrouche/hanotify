from django.db import models
from category.models import Category
from others.models import Image, SEO
from django.contrib.auth.models import User 


# Create your models here.

class Product(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(max_length=100, null=True, blank=True)
    mini_description = models.TextField(max_length=1000, null=True, blank=True)
    description = models.JSONField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount = models.TextField(max_length=50, null=True, blank=True)
    sku = models.CharField(max_length=50, null=True, blank=True)
    barcode = models.CharField(max_length=20, null=True, blank=True)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    brand = models.CharField(max_length=50, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    seo = models.OneToOneField(SEO, null=True, blank=True, on_delete=models.SET_NULL)
    specs = models.JSONField(null=True, blank=True)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,  related_name='images')
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    index = models.SmallIntegerField()

class ProductMainImage(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='main_image')
    image = models.ForeignKey(ProductImage, on_delete=models.SET_NULL, null=True)

variant_choices=(
    ('dropdown', 'Dropdown'),
    ('text-button', 'Text button'),
    ('colored-circle', 'Colored circle'),
    ('radio-button', 'Radio button'),
    ('image-with-text', 'Image with text'),
)

class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,  related_name='variants')
    name = models.CharField(max_length=20)
    type = models.CharField(max_length=20, choices=variant_choices) 

class VariantOption(models.Model):
    name = models.CharField(max_length=20, null=True, blank=True)
    color= models.CharField(max_length=6, null=True, blank=True)
    image = models.OneToOneField(Image, on_delete=models.CASCADE, null=True, blank=True)

class ProductVariantCombination(models.Model):
    product = models.ForeignKey(Product, related_name='variant_combinations', on_delete=models.CASCADE)
    variant_options = models.ManyToManyField(VariantOption)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {', '.join(option.name for option in self.variant_options.all())}"

    class Meta:
        unique_together = ('product', 'price')  # Ensures unique combination for a specific product

class RelatedProduct(models.Model):
    main_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='related_products')
    related_products = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='products_related_to')
    order = models.PositiveIntegerField()
