from . import views
from django.urls import path

urlpatterns = [
    path('initiate-product', views.initiate_product),
]