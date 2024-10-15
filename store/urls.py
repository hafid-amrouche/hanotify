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
        path('update-store-info', views.update_store_info),
        path('non-selected-top-pick-products', views.non_selected_products_container_products),
        path('non-selected-category-products', views.non_selected_category_products),
        path('update-homepage', views.update_homepage),
        path('home-customization-products', views.home_customization_products),
        path('get-store-credit', views.get_store_credit),
        path('get-default-shipping-costs', views.get_default_shipping_cost),
        path('toggle-auto-home-page', views.toggle_auto_home_page),

        # hanotify.store
        path('get-sidebar-content', views.sidebar_content),
        path('home-page-sections', views.home_customization_products),
        path('store-home-page-sections', views.store_home_page_sections)

]