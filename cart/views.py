from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import View
from goods.models import *
from django.core.cache import cache
from redis import StrictRedis
from until.my_until import LoginRequireMixin


class CartaddView(View):
    def post(self, request):
        '''购物车记录添加'''
        user = request.user

        if not user.is_authenticated():
            return JsonResponse({"res": 0, "errormsg": "请登录"})

        sku_id = request.POST.get("sku_id")

        count = request.POST.get("count")

        if not all([sku_id, count]):
            return JsonResponse({"res": 1, "errormsg": "数据不完整"})

        try:
            count = int(count)
        except:
            return JsonResponse({"res": 2, "errormsg": "数目出错"})

        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except:
            return JsonResponse({"res": 3, "errormsg": "商品不存在"})

        connect = StrictRedis("192.168.12.184")
        cart_key = "cart_%d" % user.id

        cart_count = connect.hget(cart_key, sku_id)
        if cart_count:
            count += int(cart_count)

        # print(count)

        if count > sku.stock:
            return JsonResponse({"res": 4, "errormsg": "商品库存不足"})

        connect.hset(cart_key, sku_id, count)

        total_count = get_cart_count(user)
        print(total_count)

        return JsonResponse({"res": 5, "total_count": total_count, "msg": "添加成功"})


class CartInfoView(LoginRequireMixin, View):
    '''购物车页面显示'''

    def get(self, request):
        '''显示'''
        user = request.user
        connect = StrictRedis("192.168.12.184")
        cart_key = "cart_%d" % user.id
        cart_dict = connect.hgetall(cart_key)

        skus = []

        total_count = 0
        total_price = 0
        for sku_id, count in cart_dict.items():
            #根据Id获取商品信息
            sku = GoodsSKU.objects.get(id=sku_id)
            #计算小计
            sku_money = sku.price * int(count)

            #动态添加属性
            sku.sku_money = sku_money
            sku.count = count



            skus.append(sku)
            total_count += int(count)
            total_price += sku_money

        cxt = {
            "total_count": total_count,
            "total_price": total_price,
            "skus": skus,
        }
        return render(request, "cart/cart.html", cxt)


class CartcountView(View):
    '''异步给搜索页面添加数据'''

    def get(self, request):
        total_count = get_cart_count(request.user)
        return JsonResponse({"total_count": total_count})


def get_cart_count(user):
    '''获取购物车里货物的数量'''
    total_count = 0
    if user.is_authenticated():
        connect = StrictRedis("192.168.12.184")

        cart_key = "cart_%d" % user.id
        cart_dict = connect.hgetall(cart_key)

        #        遍历获取的商品信息
        for sku_id, count in cart_dict.items():
            print(sku_id, count)
            total_count += int(count)

    return total_count


class CartUpdateView(View):
    '''购物车记录的更新'''

    def post(self, request):
        user = request.user
        if not user.is_authenticated():
            return JsonResponse({"res": 0, "errormsg": "请先登录"})

        # 接收数据
        sku_id = request.POST.get("sku_id")
        count = request.POST.get("count")

        # 数据效验
        if not all([sku_id, count]):
            return JsonResponse({"res": 1, "errormsg": "数据不完整"})
        # 数目
        try:
            count = int(count)
        except:
            return JsonResponse({"res": 2, "errormsg": "数目出错"})
        # 商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except:
            return JsonResponse({"res": 3, "errormsg": "商品不存在"})
        # 连接数据库
        connect = StrictRedis("192.168.12.184")
        cart_key = "cart_%d" % user.id
        # 获取购物车中的数目/再看库存中的数目/如果购物车中的数目大于库存

        if count > sku.stock:
            return JsonResponse({"res": 4, "errormsg": "商品库存不足"})

        connect.hset(cart_key, sku_id, count)
        total_count = get_cart_count(user)

        return JsonResponse({"res": 5, "total_count": total_count, "msg": "成功"})


class CartDelView(View):
    def post(self, request):
        '''购物车记录的删除'''
        user = request.user
        if not user.is_authenticated():
            return JsonResponse({"res": 0, "errormsg": "请登录"})
        # 获取数据
        try:
            sku_id = request.POST.get("sku_id")
        except:
            return JsonResponse({"res": 1, "errormsg": "sku_id无效"})
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except:
            return JsonResponse({"res": 2, "errormsg": "商品不存在"})

        connect = StrictRedis("192.168.12.184")
        cart_key = "cart_%d" % user.id

        connect.hdel(cart_key, sku_id)

        # 计算用户购物车中商品总件数
        total_count = get_cart_count(user)
        print(total_count)

        return JsonResponse({"res": 3, "total_count": total_count, "msg": "删除成功"})
