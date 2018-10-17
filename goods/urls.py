# coding=utf-8
from django.conf.urls import url
from user import views

urlpatterns = [
    url(r'^index/$', views.IndexView.as_view(), name="index"),

    url(r'^detail/$', views.IndexView.as_view(), name="detail"),
    url(r'^list/$', views.IndexView.as_view(), name="list"),

]


