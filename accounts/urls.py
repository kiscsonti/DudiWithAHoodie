from django.conf.urls import url
from django.contrib.auth.views import login, logout
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    url(r'^$', views.temp, name='temp'),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'logged_out.html'}, name='logout'),
]