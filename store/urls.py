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
        path('set-up-fb-pixel', views.set_up_fb_pixel),
        path('get-fb-pixel', views.get_fb_pxel),
        path('delete-fb-pixel', views.delete_fb_pixel),
        path('set-up-tiktok-pixel', views.set_up_tiktok_pixel),
        path('get-tiktok-pixel', views.get_tiktok_pixels),
        path('delete-tiktok-pixel', views.delete_tiktok_pixel),
        path('set-up-conversions-api', views.set_up_conversion_api_token),
        path('delete-conversions-api', views.delete_conversion_api_token),
        path('set-up-test-event-code', views.set_up_test_code_event),
        path('update-store-info', views.update_store_info)
]