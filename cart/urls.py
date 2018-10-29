# coding=utf-8
from django.conf.urls import url
from cart import views

urlpatterns = [
    url(r'^add/$', views.CartaddView.as_view(), name="add"),
    url(r'^count/$', views.CartcountView.as_view(), name="count"),
    url(r'^delete/$', views.CartDelView.as_view(), name="delete"),
    url(r'^update/$', views.CartUpdateView.as_view(), name="update"),
    url(r'^cartinfo/$', views.CartInfoView.as_view(), name="cartinfo"),
]


