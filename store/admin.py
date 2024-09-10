from django.contrib import admin
from .models import Store, StateShippingCost, Status, Visitor, IpAddress, GSInfo, VIPStore, Domain, FBPixel, TikTokPixel
# Register your models here.

admin.site.register(Store)
admin.site.register(StateShippingCost)
admin.site.register(Status)
admin.site.register(Visitor)
admin.site.register(IpAddress)
admin.site.register(GSInfo)
admin.site.register(VIPStore)
admin.site.register(Domain)
admin.site.register(FBPixel)
admin.site.register(TikTokPixel)

