from django.contrib import admin
from goods.models import *

# Register your models here.


admin.site.register(GoodsSKU)
admin.site.register(Goods)
admin.site.register(GoodsType)
admin.site.register(GoodsImage)
admin.site.register(IndexGoodBanner)
admin.site.register(IndexTypeGoodsBanner)
admin.site.register(IndexPromotionBanner)