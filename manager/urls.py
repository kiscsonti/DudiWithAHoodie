from django.conf.urls import url

from . import views

urlpatterns = [

    url(r'^$', views.bejegyzes, name="main_page"),
]