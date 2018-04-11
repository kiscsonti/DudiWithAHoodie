from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User

from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os

# Create your models here.

fs = FileSystemStorage(location=settings.MEDIA_ROOT)

file_formats = ['MOV', 'MPEG4', 'MP4', 'AVI', 'WMV']

def validate_file_extension(value):
    extension = value.name.split()[-1]
    if extension not in file_formats:
        raise ValidationError(u'Not supported extension' + extension + '. Please use ' + file_formats + ' format.')


def name_file_as_videoid(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.id, ext)
    return os.path.join(filename)



class Video(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=100)
    filename = models.FileField(storage=fs, default='ERROR', validators=[validate_file_extension], upload_to=name_file_as_videoid)
    create_date = models.DateField(auto_now_add=True)
    create_time = models.TimeField(auto_now_add=True)
    is_commentable = models.BooleanField(default=True)


class Category(models.Model):
    name = models.CharField(max_length=50)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    video_id = models.ForeignKey(Video, on_delete=models.CASCADE)
    create_date = models.DateField(auto_now_add=True)
    create_time = models.TimeField(auto_now_add=True)
    content = models.CharField(max_length=500)

    class Meta:
        unique_together = (("user", "video_id"),)


class VideoKategoria(models.Model):
    video_id = models.ForeignKey(Video, models.DO_NOTHING)
    kat_id = models.ForeignKey(Category, models.CASCADE)

    class Meta:
        unique_together = (("video_id", "kat_id"),)


class Watched(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
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
