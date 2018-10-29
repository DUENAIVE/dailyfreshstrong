from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.generic import View
from goods.models import *
from user.models import User_Site
from django.core.cache import cache
from redis import StrictRedis
from until.my_until import LoginRequireMixin
from django.core.urlresolvers import reverse
from order.models import *
import datetime
from django.db import transaction
import os
from django.conf import settings
from alipay import AliPay


# Create your views here.
class OrderView(LoginRequireMixin, View):
    def post(self, request):
        '''提交订单页面显示'''
        # 获取登录用户
        user = request.user
        # 获取参数sku_ids
        sku_ids = request.POST.getlist("sku_ids")
        # 效验参数
        if not sku_ids:
            return redirect(reverse("cart:cartinfo"))
        connect = StrictRedis("192.168.12.184")
        cart_key = "cart_%d" % user.id
        skus = []
        total_count = 0
        total_price = 0
        # 遍历sku_ids获取用户所买卖商品的信息
        for sku_id in sku_ids:
            sku = GoodsSKU.objects.get(id=sku_id)
            # 获取所买商品的数量
            count = connect.hget(cart_key, sku_id)
            # 计算商品小计
            amount = sku.price * int(count)
            # 动态给sku添加属性来保存商品的数量
            sku.count = count
            # 动态给商品添加小计属性,保存商品上的小计
            sku.amount = amount
            # 将所有商品保存到列表中

            skus.append(sku)
            # 累加计算商品的总计件数和总价格


            total_count += int(count)
            total_price += amount

        # 运费
        transform_price = 10
        # 组织上下文
        # 实付款
        total_pay = total_price + transform_price
        # 获取用户的收货地址
        addrs = User_Site.objects.filter(user=user, is_defaule=True)
        sku_ids = ','.join(sku_ids)
        cxt = {
            "skus": skus,
            "total_count": total_count,
            "total_price": total_price,
            "transform_price": transform_price,
            "total_pay": total_pay,
            "addrs": addrs,
            "sku_ids": sku_ids
        }

        return render(request, "order/place_order.html", cxt)


class CommitView(LoginRequireMixin, View):
    @transaction.atomic
    def post(self, request):
        addr_id = request.POST.get("addr_id")
        pay_style = request.POST.get("pay_style")
        sku_ids = request.POST.get("sku_ids")
        user = request.user
        print(sku_ids)
        if not user.is_authenticated():
            return JsonResponse({'res': 0, 'errmsg': '请登录'})

        if not all([addr_id, pay_style, sku_ids]):
            return JsonResponse({'res': 1, 'errmsg': '参数错误'})

        try:
            pay_style = int(pay_style)

        except:
            return JsonResponse({'res': 2, 'errmsg': '非法支付方式'})

        if pay_style not in dict(OrderInfo.PAY_METHOD_CHOICES).keys():
            return JsonResponse({'res': 2, 'errmsg': '非法支付方式'})

        try:
            addr = User_Site.objects.get(id=addr_id)
        except:
            return JsonResponse({'res': 3, 'errmsg': '地址非法'})

        # 订单id
        order_id = datetime.datetime.today().strftime("%Y%m%d%H%M%S") + str(user.id)
        # 运费
        transform_price = 10
        # 总数目总金额
        total_count = 0
        total_price = 0
        # #开启redis
        try:
            # 在增删改处设置保存点
            save_point = transaction.savepoint()

            order = OrderInfo.objects.create(
                order_id=order_id,
                user=user,
                addr=addr,
                pay_method=pay_style,
                total_price=total_price,
                total_count=total_count,
                transit_price=transform_price
            )

            connect = StrictRedis("192.168.12.184")

            cart_key = "cart_%d" % user.id

            sku_ids = sku_ids.split(",")
            for sku_id in sku_ids:
                for i in range(3):
                    try:
                        sku = GoodsSKU.objects.get(id=sku_id)
                        old_stock = sku.stock
                        # 悲观锁
                        # sku=GoodsSKU.objects.select_for_update().get(id=sku_id)
                    except:
                        return JsonResponse({"res": 4, "errmsg": "商品不存在"})

                    # 从redis中获取用户所需要购买的数量
                    count = connect.hget(cart_key, sku_id)
                    # 判断库存
                    if int(count) > sku.stock:
                        return JsonResponse({"res": 6, "errmsg": "库存不足"})

                    current_stock = old_stock - int(count)

                    num = GoodsSKU.objects.filter(id=sku_id, stock=old_stock).update(stock=current_stock)
                    if num == 0:
                        if i == 2:
                            transaction.savepoint_rollback(save_point)
                            return JsonResponse({"res": 8, "errmsg": "000000000000"})
                        continue

                    # 再向df_order_goods表中添加记录
                    OrderGoods.objects.create(order=order, sku=sku, count=count, price=sku.price)
                    # 更新商品的库存和销量
                    sku.stock -= int(count)
                    sku.sales += int(count)
                    # 累加计算商品的总数量和总价格
                    amount = sku.price * int(count)
                    total_count += int(count)
                    total_price += amount
                    break
            # 更新订单信息表中的商品的总数量和总价格
            order.total_count = total_count
            order.total_price = total_price
            order.save()
            # 同生共死代码全部完成后就进行事务提交
            # 提交事务
            transaction.savepoint_commit(save_point)


        except:
            # 出现异常就回滚
            # 回滚是数据库端的操作,代码会照常进行
            transaction.savepoint_rollback(save_point)
            return JsonResponse({"res": 7, "errmsg": "下单失败"})

        connect.hdel(cart_key, *sku_ids)
        return JsonResponse({"res": 5, "msg": "下单成功"})


class AliPayView(LoginRequireMixin, View):
    def post(self, request):
        # 用户是否登录
        user = request.user
        if not user.is_authenticated():
            return JsonResponse({"res": 0, "errmsg": "登陆后请重试"})
        order_id = request.POST.get("order_id")
        # 效验00参数
        if not order_id:
            return JsonResponse({"res": 1, "errmsg": "无效的订单id"})

        try:
            print('order_id:%s' % order_id)
            order = OrderInfo.objects.get(order_id=order_id, user_id=user.id, pay_method=3, order_status=1)


        except OrderInfo.DoesNotExist as e:
            print(e)
            return JsonResponse({"res": 2, "errmsg": "订单错误"})

        # 业务处理:使用python sdk调用支付宝的支付接口
        # 初始化
        # app_private_key_string = os.path.join(settings.BASE_DIR, )
        # alipay_public_key_string = os.path.join(settings.BASE_DIR, )
        app_private_key_string = open("cart/migrations/app_private_key.pem").read()
        alipay_public_key_string = open("cart/migrations/app_public_key.pem").read()

        alipay = AliPay(
            appid="2016092000554978",
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False
        )
        print(alipay)
        subject = "dailyfresh-%s" % order.order_id
        print(subject)
        total_pay = order.total_price + order.transit_price

        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(total_pay),
            subject=subject,
            return_url=None,
            notify_url=None  # 可选, 不填则使用默认notify url
        )
        print(order_string)
        pay_url = "https://openapi.alipaydev.com/gateway.do?" + order_string
        return JsonResponse({"res": 3, "pay_url": pay_url})


class CheckPayView(LoginRequireMixin, View):
    def post(self, request):
        # 用户是否登录
        user = request.user
        if not user.is_authenticated():
            return JsonResponse({"res": 0, "errmsg": "登陆后请重试"})
        order_id = request.POST.get("order_id")
        # 效验00参数
        if not order_id:
            return JsonResponse({"res": 1, "errmsg": "无效的订单id"})

        try:
            print('order_id:%s' % order_id)
            order = OrderInfo.objects.get(order_id=order_id, user_id=user.id, pay_method=3, order_status=1)


        except OrderInfo.DoesNotExist as e:
            print(e)
            return JsonResponse({"res": 2, "errmsg": "订单错误"})

        # 业务处理:使用python sdk调用支付宝的支付接口
        # 初始化
        # app_private_key_string = os.path.join(settings.BASE_DIR, )
        # alipay_public_key_string = os.path.join(settings.BASE_DIR, )
        app_private_key_string = open("cart/migrations/app_private_key.pem").read()
        alipay_public_key_string = open("cart/migrations/app_public_key.pem").read()

        alipay = AliPay(
            appid="2016092000554978",
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False
        )
        while True:
            response = alipay.api_alipay_trade_query(order_id)
            code = response.get("code")
            print("code:%s"%code)

            if code == '10000' and response.get('trade_status') == 'TRADE_SUCCESS':
                # 支付成功

                # 获取支付宝交易账号
                trade_no = response.get("trade_no")
                # 更新订单状态
                order.trade_no = trade_no
                order.order_status = 4#待评价
                order.save()
                # 返回结果
                return JsonResponse({"res": 3, "msg": "支付成功"})
            elif code=="40004" or (code == '10000' and response.get("trade_status") == "WAIT_BUYER_PAY"):
                import time
                print("三秒后再次查询订单状态")
                time.sleep(3)
                continue
            else:
                return JsonResponse({"res":4,"errmsg":"支付出错"})





