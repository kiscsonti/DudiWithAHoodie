from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Video(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL)
    title = models.CharField(max_length=100)
    create_date = models.DateField(auto_now_add=True)
    create_time = models.TimeField(auto_now_add=True)
    is_commentable = models.BooleanField(default=True)



class Category(models.Model):
    name = models.CharField(max_length=50)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL)
    video_id = models.ForeignKey(Video, on_delete=models.CASCADE)
    create_date = models.DateField(auto_now_add=True)
    create_time = models.TimeField(auto_now_add=True)
    content = models.CharField(max_length=500)

    class Meta:
        unique_together = (("user", "video_id"),)

class VideoKategori(models.Model):
    video_id = models.ForeignKey(Video, models.DO_NOTHING)
    kat_id = models.ForeignKey(Category, models.CASCADE)

    class Meta:
        unique_together = (("video_id", "kat_id"),)


class Watched(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL)
    video_id = models.ForeignKey(Video, on_delete=models.CASCADE)
    watched_date = models.DateField(auto_now_add=True)
    watched_time = models.TimeField(auto_now_add=True)


class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=False, blank=False)

class list_videos(models.Model):
    list_id = models.ForeignKey(Playlist, models.CASCADE)
    video_id = models.ForeignKey(Video, models.CASCADE)

    class Meta:
        unique_together = (("list_id", "video_id"),)


