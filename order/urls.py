# coding=utf-8
from django.conf.urls import url
from order import views

urlpatterns = [
    url(r'^place', views.OrderView.as_view(), name="place"),
    url(r'^commit', views.CommitView.as_view(), name="commit"),
    url(r'^pay', views.AliPayView.as_view(), name="pay"),
    url(r'^check', views.CheckPayView.as_view(), name="check"),


]


