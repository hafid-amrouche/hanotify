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
            design = default_design
        )
        
post_save.connect(home_page_post_create, HomePage)



# from store.models import Store, DefaultPageSection
# default_design = {
#             "mobile": {
#                 "marginTop": 4,
#                 "marginHorizontal": 4,
#                 "backgroundColor": {
#                     "light": "#00000000",
#                     "dark": "#121212"
#                 },
#                 "title": {
#                     "showTitle": True,
#                     "size": 26,
#                     "direction": "center",
#                     "bordersRounded": None,
#                     "padding": 0,
#                     "label": {
#                         "color": {
#                             "light": "#72543c",
#                             "dark": "#bca08a"
#                         }
#                     }
#                 },
#                 "products": {
#                     "productsDisplay": "simple",
#                     "justifyContent": "center",
#                     "gap": 8,
#                     "bordersRounded": True,
#                     "borderWidth": 1,
#                     "backgroundColor": {
#                         "light": "#00000000",
#                         "dark": "#121212"
#                     },
#                     "borderColor": {
#                         "light": "#80808060",
#                         "dark": "#50505080"
#                     },
#                     "product": {
#                         "width": "50%",
#                         "image": {
#                             "objectFit": "cover",
#                             "aspectRatio": "1/1"
#                         },
#                         "title": {
#                             "size": 18,
#                             "color": {
#                                 "light": "#11181C",
#                                 "dark": "#ffffff"
#                             }
#                         },
#                         "price": {
#                             "size": 18,
#                             "color": {
#                                 "light": "#754f32",
#                                 "dark": "#bca08a"
#                             }
#                         }
#                     }
#                 }
#             },
#             "PC": {
#                 "marginTop": 10,
#                 "marginHorizontal": 8,
#                 "backgroundColor": {
#                     "light": "#00000000",
#                     "dark": "#121212"
#                 },
#                 "title": {
#                     "showTitle": True,
#                     "size": 23,
#                     "direction": "start",
#                     "padding": 8,
#                     "label": {
#                         "color": {
#                             "light": "#bca08a",
#                             "dark": "#bca08a"
#                         }
#                     }
#                 },
#                 "products": {
#                     "productsDisplay": "simple",
#                     "justifyContent": "center",
#                     "gap": 8,
#                     "borderWidth": 1,
#                     "backgroundColor": {
#                         "light": "#00000000",
#                         "dark": "#121212"
#                     },
#                     "borderColor": {
#                         "light": "#80808060",
#                         "dark": "#50505080"
#                     },
#                     "product": {
#                         "width": "220px",
#                         "image": {
#                             "aspectRatio": "1/1",
#                             "objectFit": "cover"
#                         },
#                         "title": {
#                             "size": 22,
#                             "color": {
#                                 "light": "#11181C",
#                                 "dark": "#ffffff"
#                             }
#                         },
#                         "price": {
#                             "size": 16,
#                             "color": {
#                                 "light": "#754f32",
#                                 "dark": "#bca08a"
#                             }
#                         }
#                     },
#                     "bordersRounded": False
#                 }
#             }
# }

# for store in Store.objects.all():
#     DefaultPageSection.objects.create(
#         home_page = store.home_page,
#         design = default_design,
#     )