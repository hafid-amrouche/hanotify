from django.contrib import admin
from .models import Product, RelatedProduct, StateShippingCost, VariantsCombination

# Register your models here.

admin.site.register(Product)
admin.site.register(RelatedProduct)
admin.site.register(StateShippingCost)
admin.site.register(VariantsCombination)