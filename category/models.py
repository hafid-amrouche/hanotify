from django.db import models
from django.contrib.auth.models import User 
from store.models import Store, HomePageSection
from django.db.models.signals import post_save



# Create your models here.

class Category(models.Model):
    active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='categories') # remove blank
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True, related_name='categories') # remove blank
    label = models.CharField(max_length=50)
    image = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True, max_length=1000)
    slug = models.SlugField(null=True, blank=True)
    class Meta:
        ordering = ['-id']  # Default ordering: newest orders first

def category_post_create(sender, instance, created,  **kwargs):
    category = instance
    if created:
        HomePageSection.objects.create(
            home_page = category.store.home_page,
            section_id = f'category-{category.id}',
            type = 'category',
            design = None,
            category = category,
        )
post_save.connect(category_post_create, Category)

class CategoryPreviewProduct(models.Model):
    category =  models.ForeignKey(Category, on_delete=models.CASCADE, related_name='preview_products')
    product = models.ForeignKey('product.product', on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField()

