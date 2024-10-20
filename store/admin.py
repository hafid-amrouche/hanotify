from django.contrib import admin
from .models import (Store, StateShippingCost, Status, Visitor, 
    IpAddress, GSInfo, Domain, FBPixel, TikTokPixel, ConversionsApi, HomePage, HomePageSection, DefaultPageSection)
# Register your models here.

admin.site.register(Store)
admin.site.register(StateShippingCost)
admin.site.register(Status)
admin.site.register(Visitor)
admin.site.register(IpAddress)
admin.site.register(GSInfo)
admin.site.register(Domain)
admin.site.register(FBPixel)
admin.site.register(ConversionsApi)
admin.site.register(TikTokPixel)
admin.site.register(HomePageSection)
admin.site.register(HomePage)
admin.site.register(DefaultPageSection)
