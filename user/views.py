# coding-utf-8
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from user.models import *
from django.views.generic import View
from io import BytesIO
from dailyfresh import settings
from django.core.mail import send_mail
from mycelery.celery_task import *
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
# Create your views here.
import re
import random
from PIL import ImageFont, ImageDraw, ImageFilter, ImageColor, Image
from django.contrib.auth import authenticate, login, logout
from until.my_until import LoginRequireMixin
from order.models import *


class RegisterView(View):
    def get(self, request):
        return render(request, "user/register.html")

    def post(self, request):
        request_info = request.POST
        username = request_info.get("user_name")
        pwd = request_info.get("pwd")
        pwd2 = request_info.get("cpwd")
        uemail = request_info.get("email")
        allow = request_info.get("allow")
        # 错误信息回显
        error = {}
        if not all([username, pwd, pwd2, uemail]):
            error["name_error"] = "数据不完整"
            return render(request, "user/register.html", {"error_msg": error})
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', uemail):
            error["email_error"] = "邮箱不匹配"
        if len(pwd) < 8 or len(pwd) > 20:
            error["pwd_error"] = "请输入8到20位的密码"
        if len(username) < 5 or len(username) > 20:
            error["name_error"] = "请输入5到20个字符的用户名"
        if allow != 'on':
            error["allow_error"] = "请同意协议"
        try:
            user = User.objects.filter(username=username)
        except User.DoesNotExist:
            user = None
        if user:
            error["name_error"] = "用户名已存在"
        if pwd != pwd2:
            error["pwd_error"] = "两次密码不一致"

        if error:
            return render(request, "user/register.html", {"error": error})
        else:

            user = User.objects.create_user(username=username, password=pwd, email=uemail)
            user.is_active = 0
            user.save()
            # 发送激活邮件,包含激活链接:http://ip:port/user/active/41,激活链接中要包含用户的身份信息
            # 并且要将用户信息加密
            serializer = Serializer(settings.SECRET_KEY, 1000)  # 设置一个key过期时间为1000s
            info = {"confire": user.id}  # 将user.id设置为要加密的信息
            token = serializer.dumps(info).decode()  # 将id加密
            # 拼接路径发送邮件
            encryption_url = "http://192.168.12.184:3333/user/active/%s" % token
            # 发邮件
            subject = "天天生鲜欢迎你"  # 信息的主题
            message = 'Welcom'
            sender = settings.EMAIL_FROM  # 发送者
            receiver = [uemail]  # 接受者可以在列表中设置多个
            # 写html消息将文字拼接到里面
            html_message = '<h1>%s,欢迎来到天天生鲜</h1>请点击链接完成注册<br/><a href="%s">%s</a>' % (
                username, encryption_url, encryption_url)
            # 使用celery中的函数发送信息,消除延迟
            send_mail_task.delay(subject, message, sender, receiver, html_message)
            return redirect(reverse('user:login'))


class ActiveView(View):
    def get(self, request, token):
        '''用户进行激活'''
        serializer = Serializer(settings.SECRET_KEY, 1000)
        try:
            info = serializer.loads(token)
            user_id = info["confire"]
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            return redirect(reverse('user:login'))
        except SignatureExpired:
            return HttpResponse("用户信息已过期,请重新注册")
        except BadSignature:
            return HttpResponse("激活链接非法,请勿相信")


class LoginView(View):
    def get(self, request):
        username = request.session.get("username", '')
        return render(request, "user/login.html", {'username': username})

    def post(self, request):
        '''登录认证'''
        request_info = request.POST
        username = request_info.get("username")
        pwd = request_info.get("pwd")
        remember = request_info.get("remember")
        validate = request_info.get("validate")
        validate_true = request.session["validate"]
        error = {}
        if validate != validate_true:
            error["error"] = "验证码错误"
        # 认证系统登录验证
        user = authenticate(username=username, password=pwd)
        if user is None:
            error["error"] = "用户名或密码错误"
        if error:
            return render(request, "user/login.html", {"error": error})
        else:
            if remember:
                request.session["username"] = username
            if user.is_active:
                # 用户激活
                # 记录用户登录状态
                login(request, user)
                next_url = request.GET.get("next")
                if next_url:
                    return redirect(next_url)
                else:
                    return redirect(reverse("goods:index"))
            else:
                error["error"] = "账号尚未激活"
                return render(request, "user/login.html", {"error": error})


class LogOutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse("user:index"))


class PwdForgetView(View):
    def get(self, request):
        return render(request, "user/pwd_forget.html")

    def post(self, request):
        request_info = request.POST
        username = request_info.get("username")
        validate = request_info.get("validate")
        user = User.objects.filter(username=username)
        validate_true = request.session["validate"]
        error = {}
        if not user:
            error["error"] = "用户不存在"
        if validate != validate_true:
            error["error"] = "验证码错误"

        if error:
            return render(request, "user/pwd_forget.html", {"error": error})
        else:
            username = user.values("username")
            request.session["username"] = username[0]["username"]
            return redirect(reverse("user:testemail"))


class TestEmailView(View):
    def get(self, request):
        return render(request, "user/test_email.html")

    def post(self, request):
        request_info = request.POST
        email = request_info.get("email")
        newpwd = request_info.get("newpwd")

        username = request.session.get("username")
        user = User.objects.get(username=username)
        # user = User.objects.create_user(username=username, password=pwd, email=uemail)
        user.set_password(newpwd)
        user.is_active = 0
        user.save()

        # 发邮件
        serializer = Serializer(settings.SECRET_KEY, 1000)
        token = serializer.dumps({"confire": user.id}).decode()
        encryption_url = "http://192.168.12.184:3333/user/active/%s" % token

        subject = "Welcome to 天天生鲜"  # 主题
        message = "welcom"
        sender = settings.EMAIL_FROM  # 谁发的
        receiver = [email]
        html_message = '<h1>%s,欢迎来到天天生鲜</h1>请点击链接完成修改密码<br/><a href="%s">%s</a>' % (
            username, encryption_url, encryption_url)
        send_mail(subject, message, sender, receiver, html_message=html_message)
        return redirect(reverse('user:login'))


class ValidateCode(View):
    def get(self, request):
        # 定义变量,画面背景色,宽高
        width = 100
        height = 25
        bgcolor = (random.randint(20, 255), random.randint(20, 100), 255)
        # 创建画面对象
        image = Image.new("RGB", (width, height), bgcolor)
        # 创建画笔对象
        draw = ImageDraw.Draw(image, )
        # 调用画笔的point函数绘制噪点
        for i in range(0, width, 2):
            for j in range(0, height, 2):
                draw.point((i, j), fill=(random.randint(0, 255), random.randint(0, 255), 255))
        # 定义验证码被选值    随机选取四个值作为验证码
        random_str = ''
        str = 'qwertyuiopasdfgjhjklzxcvbnm123567894QWERTYUIOPSDFGHJKLZXCVBNM'
        for i in range(4):
            random_str += str[random.randrange(len(str))]
        # 将数据保存到session
        request.session["validate"] = random_str
        # 构造字体对象
        font = ImageFont.truetype("./usr/share/fonts/truetype/freefont/FreeSerifBoldItalic.ttf", 20)
        # 构造字体颜色
        fontcolor = (random.randint(100, 255), 255, random.randint(20, 255))
        # 绘制四个字draw.text()
        for i in range(4):
            draw.text((10 + 20 * i, 0), random_str[i], font=font, fill=fontcolor)
        # 释放画笔del draw
        del draw
        # 内存文件操作
        buf = BytesIO()

        # 将图片保存在内存中,文件类型一般为png
        image.save(buf, 'png')

        # 将内存中的图片数据返回给客户端
        return HttpResponse(buf.getbuffer(), 'image/png')


class UserSiteView(LoginRequireMixin, View):
    '''编辑收货信息界面'''

    def get(self, request):
        '''在页面显示所有的地址信息'''
        user_id = request.session.get("_auth_user_id")
        user_site = User_Site.objects.filter(user_id=user_id, is_delete=0)
        return render(request, "user/user_center_site.html", {"page": "3", "user_site": user_site})

    def post(self, request):
        # 获取现在正在登录用户的两种方法
        # 1.用户认证系统自带的在request中有user属性就是正在登录的用户
        # 2.用户认证系统中登陆的时候会将用户信息写到session中键是'_auth_user_id'
        user_id = request.session.get("_auth_user_id")
        request_info = request.POST
        # 获取前段中输入的字符串,并将它们存在数据库中
        recvname = request_info.get("recv_name")
        addr = request_info.get("addr")
        phone_num = request_info.get("phone_num")
        post_num = request_info.get("post_num")
        # 先获取id
        pro_id = request_info.get("pro")
        city_id = request_info.get("city")
        area_id = request_info.get("area")

        error = {}  # 创建错误字典将错误保存在字典中
        if not re.match(r'^1(3|4|5|7|8)\d{9}$', phone_num):
            error["phone_num_error"] = "请输入正确的电话号码"
        if not re.match(r'[0-9]{6}', post_num):
            error["post_num_error"] = "邮编错误"
            # 如果字典不为空就不保存到数据库
        #     将错误显示到编辑地址页面
        if not pro_id:
            error["pro_error"] = '请选择省'
        if not city_id:
            error["city_error"] = "请选择市"
        if not area_id:
            error["area_error"] = "请选择区(县)"
        if error:
            user_id = request.session.get("_auth_user_id")
            user_site = User_Site.objects.filter(user_id=user_id, is_delete=0)
            return render(request, "user/user_center_site.html", {"page": "3", "error": error, "user_site": user_site})
        else:
            # 将新建的信息当做默认地址
            # try:
            #     # 如果有默认地址将is_defaule设置为False
            #     user = request.user
            #     addrs = User_Site.objects.get(user=user, is_defaule=True)
            #     addrs.is_defaule = False
            #     addrs.save()
            # except:
            #     pass
            # 找出信息
            pro1 = Area.objects.get(codeid=pro_id)
            city1 = Area.objects.get(codeid=city_id)
            area1 = Area.objects.get(codeid=area_id)

            # 将信息创建到数据库中
            user_site = User_Site.objects.create(urecv=recvname, upost_num=post_num, uphone=phone_num,
                                                 uaddr='%s-%s-%s-%s' % (pro1, city1, area1, addr),
                                                 user_id=user_id)
            user_site.save()
            '''全部地址'''
            user_id = request.session.get("_auth_user_id")
            user_site = User_Site.objects.filter(user_id=user_id, is_delete=0)
            return render(request, "user/user_center_site.html", {"page": "3", "user_site": user_site})


#
class DefaultView(View):
    def get(self, request):
        rid = request.GET.get("rid")
        default_addr = User_Site.objects.get(id=rid)
        try:
            # 如果有默认地址将is_defaule设置为False
            user = request.user
            addrs = User_Site.objects.get(user=user, is_defaule=True)
            addrs.is_defaule = False
            addrs.save()
        except:
            pass
        default_addr.is_defaule = True
        default_addr.save()
        return HttpResponse("默认地址设置成功")


import json


class DeleteView(View):
    def get(self, request):
        did = request.GET.get('did')
        delete_user_addr = User_Site.objects.get(id=did)
        delete_user_addr.is_delete = 1
        delete_user_addr.save()
        user_id = request.session.get("_auth_user_id")
        user_site = User_Site.objects.filter(user_id=user_id, is_delete=0)
        return render(request, "user/user_center_site.html", {"page": "3", "user_site": user_site})


# 获取省信息
class ProView(View):
    def get(self, request):
        # 没有parent_id的就是
        prolist = Area.objects.filter(parent=0).values('cityname', 'codeid')
        # print(prolist)
        pro_list = []
        for i in prolist:
            b = {}
            b["id"] = i['codeid']
            b["proname"] = i['cityname']
            pro_list.append(b)
        cxt = {
            'pro_list': pro_list
        }
        hjson = json.dumps(cxt)
        return HttpResponse(hjson, content_type="application/json;charset=utf-8")


# 获取市信息
class CityView(View):
    def get(self, request):
        pid = request.GET.get('pid')
        citylist = Area.objects.filter(parent=pid).values('cityname', 'codeid')
        # print(citylist)
        city_list = []
        for i in citylist:
            b = {}
            b["id"] = i['codeid']
            b["cityname"] = i['cityname']
            city_list.append(b)
        cxt = {
            'city_list': city_list
        }
        hjson = json.dumps(cxt)
        return HttpResponse(hjson, content_type="application/json;charset=utf-8")


# 获取县/区
class AreaView(View):
    def get(self, request):
        cid = request.GET.get('cid')
        arealist = Area.objects.filter(parent=cid).values('cityname', 'codeid')
        # print(arealist)
        area_list = []
        for i in arealist:
            b = {}
            b["id"] = i['codeid']
            b["areaname"] = i['cityname']
            area_list.append(b)
        cxt = {
            'area_list': area_list
        }
        hjson = json.dumps(cxt)
        return HttpResponse(hjson, content_type="application/json;charset=utf-8")


from redis import StrictRedis
from goods.models import *


class UserInfoView(LoginRequireMixin, View):
    '''用户信息界面'''

    def get(self, request):
        user_id = request.session.get("_auth_user_id")
        user = User.objects.get(id=user_id)
        username = user.username
        email = user.email
        user = request.user
        try:
            addrs = User_Site.objects.get(user=user, is_defaule=True)
        except:
            addrs = None
        # print(addrs)
        phone_num = addrs.uphone
        addr = addrs.uaddr
        connect = StrictRedis("192.168.12.184")
        history_key = "history_%d" % request.user.id
        history = connect.lrange(history_key, 0, -1)

        # his_goods = GoodsSKU.objects.filter(id__in=history)

        try:
            his_goods = [GoodsSKU.objects.get(id=i) for i in history]
        except:
            his_goods = None
        print(his_goods)

        cxt = {

            "username": username,
            "email": email,
            "phone_num": phone_num,
            "addr": addr,
            "page": "1",
            "his_goods": his_goods
        }
        return render(request, "user/user_center_info.html", {"cxt": cxt})


from django.core.paginator import Paginator


class UserOrderView(LoginRequireMixin, View):
    '''订单界面'''

    def get(self, request, pn):
        user = request.user
        orders = OrderInfo.objects.filter(user=user).order_by("-create_time")
        for order in orders:
            # 根据order_id查询订单商品
            order_skus = OrderGoods.objects.filter(order_id=order.order_id)
            for order_sku in order_skus:
                amount = int(order_sku.count) * order_sku.price
                order_sku.amount = amount
            # 给order添加订单详情属性
            order.order_skus = order_skus

        paginator = Paginator(orders, 1)
        try:
            pn = int(pn)
        except:
            pn = 1
        if pn > paginator.num_pages:
            pn = 1
        # 获取第page页的Page实例对象
        order_page = paginator.page(pn)
        # 页码轮播控制
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif pn <= 3:
            pages = range(1, 6)

        elif num_pages - pn <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(pn - 2, pn + 3)

        # 组织上下文
        cxt = {
            "order_page": order_page,
            "pages": pages,
            "page": 2,
            'pn1': pn
        }

        return render(request, "user/user_center_order.html", cxt)
