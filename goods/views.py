from django.shortcuts import render
from django.views.generic import View
from goods.models import *


# Create your views here.
class IndexView(View):
    def get(self, request):
        # 获取商品所有种类信息
        types = GoodsType.objects.all()
        # 获取首页轮播
        goods_banner = IndexGoodBanner.objects.all().order_by("index")

        # 获取广告页面
        promotion_banner = IndexPromotionBanner.objects.all().order_by("index")

        cart_count = 0

        for type in types:
            # 过滤出图片
            image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by("index")
            # 过滤出标题
            title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by("index")

            type.image_banners = image_banners
            type.title_banners= title_banners

        cxt = {
            "types": types,
            "goods_banner": goods_banner,
            "promotion_banner": promotion_banner,
            "cart_count": cart_count

        }

        return render(request, "goods/index.html",cxt)

# class IndexView1(View):
#     def get(self,request):
#         goods_type=GoodsType.objects.all()
#         return render(request,'goods/test.html',{'good_type':goods_type})
class ListView(View):
    def get(self,request):

        return render(request,"goods/list.html")
class DetailView(View):
    def get(self,request):
        hid = request.GET.get("hid")
        sku = GoodsSKU.objects.get(id=hid)
        return render(request,"goods/detail.html",{"sku":sku})

