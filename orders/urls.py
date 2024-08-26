from django.urls import path, include
from . import views

urlpatterns = [
    path('get-orders', views.get_orders),
    path('get-abandoned-orders', views.get_abandoned_orders),
    path('get-order', views.get_order),
    path('get-abandoned-order', views.get_abandoned_order),
    path('create-order', views.create_order),
    path('update-order', views.update_order),
    path('confirm-order', views.confirm_order),
    path('change-orders-status', views.change_orders_status),
    path('delete-orders', views.delete_orders),
    path('create-user-order', views.create_user_order),
    path('update-user-order', views.update_user_order),
    path('reveal-phone-number', views.reveal_phone_number)
]