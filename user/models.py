from django.db import models
from django.contrib.auth.models import AbstractUser
from db.base_model import BaseModel


# Create your models here.
class User(AbstractUser, BaseModel):
    class Meta:
        db_table = 'df_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class User_Site(BaseModel):
    user = models.ForeignKey("User", verbose_name="用户名")
    urecv = models.CharField(max_length=40,verbose_name="收件人" )
    upost_num = models.IntegerField(null=True,verbose_name="邮编")
    uphone = models.CharField(max_length=11,verbose_name="电话号")
    uaddr = models.CharField(max_length=40,verbose_name="收件地址")
    is_defaule = models.BooleanField(default=False,verbose_name="默认收货地址")

    class Meta:
        db_table = 'df_site'
        verbose_name = '地址'
        verbose_name_plural = verbose_name


class Area(models.Model):
    codeid=models.IntegerField()
    cityname = models.CharField(max_length=20)
    parent = models.IntegerField()

    def __str__(self):
        return self.cityname
    class Meta:
        db_table='df_area'
