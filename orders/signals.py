from django.db.models.signals import post_save
from django.utils.translation import gettext as _
from .models import Order



def post_create(sender, instance, created,  **kwargs):
    order = instance
    if created:
        order.status = order.store.statuses.first()
        order.save()

post_save.connect(post_create, Order)