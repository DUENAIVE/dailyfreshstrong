import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
django.setup()


from celery import Celery
from django.core.mail import send_mail
from goods.models import *
from django.template import RequestContext,loader
from django.conf import settings



# celery -A mycelery.celery_task worker -l info

# pip freeze > ~/dailyfresh.txt 将本地虚拟环境中安装的所有软件导出
#  pip install -r ~/dailyfresh.txt -i pip源

app=Celery("mycelery.celery_task",broker="redis://192.168.12.184:6379/3")

@app.task
def send_mail_task(subject, message, sender, receiver, html_message):
    send_mail(subject, message, sender, receiver, html_message=html_message)

@app.task
def task_generate_static_index():
    '''产生首页静态页面'''
    print("生成静态页面.....")
    #获取全部种类信息
    types=GoodsType.objects.all()
    #获取首页轮播图信息
    goods_banner=IndexGoodBanner.objects.all().order_by("index")
    #获取首页促销活动信息
    promotion_banner=IndexPromotionBanner.objects.all().order_by("index")
#   获取首页分类商品展示信息
    for type in types:
        # 过滤出图片, 获取type种类首页分来商品的展示信息
        image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by("index")
        # 过滤出标题
        title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by("index")
        # 动态给type增加属性,分别保存首页分类商品展示的标题信息和图片信息
        type.image_banners = image_banners
        type.title_banners= title_banners
#       组织模板上下文
    cxt={
        "types": types,
        "goods_banner": goods_banner,
        "promotion_banner": promotion_banner,
    }
    # 使用模板
    # 1.加载模板文件,返回模板对象
    temp=loader.get_template("static_index.html")
    static_index_html=temp.render(cxt)
    save_path=os.path.join(settings.BASE_DIR,'static/html/index.html')
    with open(save_path,"w") as file:
        file.write(static_index_html)

    print("生成静态文件..................end.............")