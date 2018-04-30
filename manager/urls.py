from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^$', views.index, name="main_page"),
    url(r'^search$', views.search2, name='search'),
    url(r'^ajax/watched_video$', views.watched_video, name='watched_video'),
    url(r'^playlist/create$', views.create_playlist, name='create_playlist'),
    url(r'^add_to_playlist$', views.add_to_playlist, name='add_to_playlist'),
    url(r'^playlist/(?P<playlist_id>.+)/(?P<id>[0-9]+)', views.play_playlist, name='play_playlist'),
    #url(r'^watched(?P<videoID>.+)/(?P<userID>.+)$', views.watched, name='watched'),
    url(r'^(?P<videoID>.+)/edit$', views.edit_video, name='video_edit'),
    url(r'^(?P<videoID>.+)$', views.show_video, name='video'),

]