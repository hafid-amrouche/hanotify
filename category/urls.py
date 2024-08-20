from . import views
from django.urls import path

urlpatterns = [
    path("add-catgeory", views.addCategory),
    path("get-categories", views.get_categories),
]