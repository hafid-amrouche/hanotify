from .models import Store, Status, HomePage, DefaultPageSection
from django.db.models.signals import post_save
from django.utils.translation import gettext as _
from .constants import default_design


status_list =[
     {
        'text': 'New order',
        'icon': f'/static/icons/order-status/new-order.png',
        'order': '1',
    },
     {
        'text': 'Order confirmed',
        'icon': f'/static/icons/order-status/order-confirmed.png',
        'order': '2',
    },
    {
        'text': 'Order at shipping company',
        'icon': f'/static/icons/order-status/shipping.png',
        'order': '3',
    },
    {
        'text': 'Waiting for client to call back',
        'icon': f'/static/icons/order-status/waiting-call.png',
        'order': '4',
    },
     {
        'text': 'Order done',
        'icon': f'/static/icons/order-status/order-done.png',
        'order': '5',
    },
    {
        'text': 'Order postponded',
        'icon': f'/static/icons/order-status/postponeded.png', ##
        'order': '6',
    },
    {
        'text': 'Client out of reach',
        'icon': f'/static/icons/order-status/phone-is-off.png', ##
        'order': '7',
    },
    {
        'text': 'Client did not pick up',
        'icon': f'/static/icons/order-status/call-declined.png',
        'order': '8',
    },
    {
        'text': 'Order cancelled',
        'icon': f'/static/icons/order-status/order-canceled.png', ##
        'order': '9',
    },
     {
        'text': 'Client returned the order',
        'icon': f'/static/icons/order-status/order-returned.png', ##
        'order': '10',
    },
    {
        'text': 'Order is getting shipped back',
        'icon': f'/static/icons/order-status/order-returned-shipping.png', ##
        'order': '10',
    },
    {
        'text': 'Order returned',
        'icon': f'/static/icons/order-status/returned.png', ##
        'order': '10',
    },
   
]


def store_post_create(sender, instance, created,  **kwargs):
    if created:
        store = instance
        HomePage.objects.create(
            store=store,
            general_design= {
                'id': 'general-design',
                'type': 'general-design',
                'mobile': {
                    'backgroundColor': {
                        "light": "#ffffff",
                        "dark": "#121212"
                    }
                },
                'PC': {
                    'backgroundColor': {
                        "light": "#ffffff",
                        "dark": "#121212"
                    }
                },
            }
        )
      
        for status in status_list:
            Status.objects.create(
                store= store,
                text = status['text'],
                order=status['order'],
                icon=status['icon']
            )
        

        
post_save.connect(store_post_create, Store)

def home_page_post_create(sender, instance, created,  **kwargs):
    if created:
        home_page = instance
        DefaultPageSection.objects.create(
            home_page = home_page,  
            design = default_design()
        )
        
post_save.connect(home_page_post_create, HomePage)