from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^$', views.bejegyzes, name="main_page"),
    url(r'^(?P<videoID>.+)$', views.show_video, name='video'),
]