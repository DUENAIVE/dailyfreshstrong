from django.db import models


# Create your models here.
class User(models.Model):
    uname = models.CharField(max_length=20, unique=True, null=False)
    upwd = models.CharField(max_length=40, null=False)
    uemail = models.CharField(max_length=20, null=True)
    uphone = models.CharField(max_length=11, null=True)
    urecv = models.CharField(max_length=40, null=True)
    uaddr = models.CharField(max_length=40, null=True)
