from django.urls import path
from . import views

urlpatterns = [
        path('update-shipping-costs', views.update_shipping_costs),
        path('check-visitor', views.check_visitor),
        path('block-visitor', views.block_visitor),
        path('unblock-visitor', views.unblock_visitor),
        path('set-up-google-sheets', views.set_up_google_sheets),
        path('get-gs-info', views.get_gs_info),
        path('delete-gs-info', views.delete_gs_info),
]