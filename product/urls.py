from . import views
from django.urls import path

urlpatterns = [
    path('initiate-product', views.initiate_product),
    path('save-gallery', views.save_gallery),
    path('get-user-products', views.get_user_products),
    path('add-product', views.add_product),
    path('edit-product', views.edit_product),
    path('increment-product-views', views.incerement_product_views),
    path('get-related-products', views.get_related_products),
    path('get-products-for-seller', views.get_products_for_seller),
    path("toggle-product-state", views.toggle_product_state),
    path('delete-product', views.delete_product),
    path("get-product-variants", views.get_product_variants),
]