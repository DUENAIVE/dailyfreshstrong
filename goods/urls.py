# coding=utf-8
from django.conf.urls import url
from goods import views

urlpatterns = [
    url(r'^index/$', views.IndexView.as_view(), name="index"),
    url(r'^list/$', views.ListView.as_view(), name="list"),
    url(r'^detail/$', views.DetailView.as_view(), name="detail"),

]


