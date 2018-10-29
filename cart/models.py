from django.db import models

# Create your models here.
class Cart(models.Model):
    uid=models.IntegerField(verbose_name="用户id")
    gid=models.IntegerField(verbose_name="物品id")
    num=models.IntegerField(verbose_name="购物车数量")
    class Meta:
        db_table="df_cart"
        verbose_name="购物车"
        verbose_name_plural=verbose_name
