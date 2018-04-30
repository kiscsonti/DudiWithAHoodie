from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os

# Create your models here.

videofs = FileSystemStorage(location=settings.MEDIA_ROOT)
imagefs = FileSystemStorage(location=settings.MEDIA_ROOT)

file_formats = ['MOV', 'MPEG4', 'MP4', 'AVI', 'WMV', ]
image_formats = ['JPG', 'PNG']

# TODO: Most watched by categories
# TODO: Most active users
# TODO: Recommend similiar videos
# TODO: delete MP3 from the file formats, it is only for testing

def validate_file_extension(value):
    extension = value.name.split()[-1]
    if extension not in file_formats:
        raise ValidationError(u'Not supported extension' + extension + '. Please use ' + file_formats + ' format.')


def validate_image_extension(value):
    extension = value.name.split()[-1]
    if extension not in image_formats:
        raise ValidationError(u'Not supported extension' + extension + '. Please use ' + image_formats + ' format.')


def name_file_as_videoid(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.id, ext)
    return os.path.join(filename)


def name_image_as_videoid(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.id, ext)
    return os.path.join("tumbnails", filename)


def _delete_file(path):
    if os.path.isfile(path):
        os.remove(path)


class Video(models.Model):
    id = models.CharField(max_length=60, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=100)
    filename = models.FileField(storage=videofs, default='ERROR', validators=[validate_file_extension],
                                upload_to=name_file_as_videoid)
    thumbnail = models.ImageField(default="thumbnails/default.jpg", upload_to=name_image_as_videoid, validators=[validate_image_extension])
    description = models.CharField(max_length=500, blank=True, default="")
    create_date = models.DateField(auto_now_add=True)
    create_time = models.TimeField(auto_now_add=True)
    is_commentable = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    video_id = models.ForeignKey(Video, on_delete=models.CASCADE)
    create_date = models.DateField(auto_now_add=True)
    create_time = models.TimeField(auto_now_add=True)
    content = models.CharField(max_length=500)

    def __str__(self):
        return self.user.username + ": " + self.video_id.title

    class Meta:
        unique_together = (("user", "video_id", "create_date", "create_time"),)


class VideoKategoria(models.Model):
    video_id = models.ForeignKey(Video, models.CASCADE)
    kat_id = models.ForeignKey(Category, models.CASCADE)

    def __str__(self):
        return self.video_id.title + ": " + self.kat_id.name

    class Meta:
        unique_together = (("video_id", "kat_id"),)


class Watched(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    video_id = models.ForeignKey(Video, on_delete=models.CASCADE)
    watched_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + ": " + self.video_id.title


class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.user.username + ": " + self.title


class ListVideos(models.Model):
    list_id = models.ForeignKey(Playlist, models.CASCADE)
    sorszam = models.IntegerField(default='9999', )
    video_id = models.ForeignKey(Video, models.CASCADE)

    def __str__(self):
        return self.list_id.title + " <- " + self.video_id.title

    class Meta:
        unique_together = (("list_id", "video_id"),)


@receiver(models.signals.post_delete, sender=Video)
def delete_file(sender, instance, *args, **kwargs):
    if instance.filename:
        _delete_file(instance.filename.path)
