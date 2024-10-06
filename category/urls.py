from . import views
from django.urls import path

urlpatterns = [
    path("add-category", views.add_category),
    path("update-category", views.update_category),
    path("get-categories", views.get_categories),
    path("delete-category", views.delete_category),
    path("category-page", views.category_page),
]