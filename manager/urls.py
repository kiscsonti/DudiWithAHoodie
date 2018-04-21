from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^$', views.index, name="main_page"),
    url(r'^search$', views.search, name='search'),
    url(r'^ajax/watched_video$', views.watched_video, name='watched_video'),
    url(r'^watched(?P<videoID>.+)/(?P<userID>.+)$', views.watched, name='watched'),
    url(r'^(?P<videoID>.+)/edit$', views.edit_video, name='video_edit'),
    url(r'^(?P<videoID>.+)$', views.show_video, name='video'),

]