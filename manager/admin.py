from django.contrib import admin
from .models import Video, VideoKategoria, Playlist, Watched, Comment, Category, ListVideos
# Register your models here.


admin.site.register(Video)
admin.site.register(VideoKategoria)
admin.site.register(Playlist)
admin.site.register(Watched)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(ListVideos)
