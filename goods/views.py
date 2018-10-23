from django.shortcuts import render
from django.views.generic import View
from goods.models import *
from django.core.cache import cache
from redis import StrictRedis


# Create your views here.
class IndexView(View):
    def get(self, request):

        cxt = cache.get("cxt_cache")
        if not cxt:
            # 获取商品所有种类信息
            types = GoodsType.objects.all()
            # 获取首页轮播
            goods_banner = IndexGoodBanner.objects.all().order_by("index")

            # 获取广告页面
            promotion_banner = IndexPromotionBanner.objects.all().order_by("index")

            for type in types:
                # 过滤出图片
                image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by("index")
                # 过滤出标题
                title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by("index")

                type.image_banners = image_banners
                type.title_banners = title_banners

            cxt = {
                "types": types,
                "goods_banner": goods_banner,
                "promotion_banner": promotion_banner,
            }
            cache.set("cxt_cache", cxt, 3600)
            print("设置缓存")
        cart_count = 0
        cxt["cart_count"] = cart_count

        return render(request, "goods/index.html", cxt)


# class IndexView1(View):
#     def get(self,request):
#         goods_type=GoodsType.objects.all()
#         return render(request,'goods/test.html',{'good_type':goods_type})
class ListView(View):
    def get(self, request):
        return render(request, "goods/list.html")


class DetailView(View):
    def get(self, request):
        hid = request.GET.get("hid")
        sku = GoodsSKU.objects.get(id=hid)
        # 获取分类的所有信息
        types = GoodsType.objects.all()
        # 获取最晚增加的两个商品
        newadd = GoodsSKU.objects.filter(type_id=sku.type_id).exclude(id=hid).order_by("-create_time")[:2]
        # 获取同一spu的其他商品
        same_spu = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=hid)

        # 判断用户是否登录
        if request.user.is_authenticated():
            #     添加用户浏览记录
            connect = StrictRedis("192.168.12.184")
            history_key = "history_%s" % request.user.id
            #    移除表中的重复数据
            connect.lrem(history_key, 0, hid)
            connect.lpush(history_key, hid)
            connect.ltrim(history_key, 0, 4)
        cart_count = 0

        cxt = {
            "cart_count":cart_count,
            "sku": sku,
            "types": types,
            "newadd": newadd,
            "same_spu":same_spu
        }

        return render(request, "goods/detail.html", cxt)
