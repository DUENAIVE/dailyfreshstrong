# coding=utf-8
from django.conf.urls import url
from user import views

urlpatterns = [
    url(r'^register/$', views.RegisterView.as_view(), name="register"),
    url(r'^pwdforget/$', views.PwdForgetView.as_view(), name="pwdforget"),
    url(r'^testemail/$', views.TestEmailView.as_view(), name="testemail"),
    url(r'^login/$', views.LoginView.as_view(), name="login"),
    url(r'^loginout/$', views.LogOutView.as_view(), name="loginout"),
    url(r'^user_site/$', views.UserSiteView.as_view(), name="user_site"),
    url(r'^user_info/$', views.UserInfoView.as_view(), name="user_info"),
    url(r'^user_order/$', views.UserOrderView.as_view(), name="user_order"),
    url(r'^active/(?P<token>.*)/$', views.ActiveView.as_view(), name="active"),
    url(r'^validate_code/$', views.ValidateCode.as_view(), name="validate_code"),
    url(r'^pro/$',views.ProView.as_view(),name="pro"),
    url(r'^city/$',views.CityView.as_view(),name="city"),
    url(r'^area/$',views.AreaView.as_view(),name="area"),
    url(r'^default/$',views.DefaultView.as_view(),name="default"),
    url(r'^delete/$',views.DeleteView.as_view(),name="delete"),
]


