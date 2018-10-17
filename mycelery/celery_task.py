from celery import Celery
from django.core.mail import send_mail

import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")


# celery -A mycelery.celery_task worker -l info

# pip freeze > ~/dailyfresh.txt 将本地虚拟环境中安装的所有软件导出
#  pip install -r ~/dailyfresh.txt -i pip源

app=Celery("mycelery.celery_task",broker="redis://192.168.12.184:6379/3")




@app.task
def send_mail_task(subject, message, sender, receiver, html_message):
    send_mail(subject, message, sender, receiver, html_message=html_message)