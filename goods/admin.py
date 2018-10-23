from django.contrib import admin
from goods.models import *
from django.core.cache import cache
# Register your models here.

class GoodsSKUAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        print("baocun")
        from mycelery.celery_task import task_generate_static_index
        task_generate_static_index.delay()
        cache.delete("cxt_cache")



    def delete_model(self, request, obj):

        super().delete_model(request, obj)
        from mycelery.celery_task import task_generate_static_index
        task_generate_static_index.delay()
        cache.delete("cxt_cache")

admin.site.register(GoodsSKU,GoodsSKUAdmin)
admin.site.register(Goods)
admin.site.register(GoodsType)
admin.site.register(GoodsImage)
admin.site.register(IndexGoodBanner)
admin.site.register(IndexTypeGoodsBanner)
admin.site.register(IndexPromotionBanner)