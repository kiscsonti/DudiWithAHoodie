from .models import Watched, VideoKategoria, Video, Comment
from django.utils import timezone
from datetime import datetime, timedelta
import shortuuid



def get_after_date(items, days):
    """items => video id-k"""
    if days == -1:
        return get_data_from_video_ids(items)

    time_threshold = timezone.now() - timedelta(days=days)
    result = []
    for item in items:
        if Video.objects.get(pk=item).create_datetime >= time_threshold:
            result.append(item)

    return get_data_from_video_ids(result)


def get_data_from_video_ids(videos, asString=True):
    views = []
    tags = []
    vidik = []
    for video in videos:
        views.append(get_watched_counter(video))
        tags.append(get_video_categories(video, asString=asString))
        vidik.append(Video.objects.get(id=video))

    return zip(vidik, views, tags)


def get_days(date):
    if date == "Day":
        return 1
    elif date == "Month":
        return 30
    elif date == "Year":
        return 365
    else:
        return -1


def get_watched_counter(videoID):
    return Watched.objects.filter(video_id=videoID).count()


def get_video_categories(videoID, asString=False):
    cats = VideoKategoria.objects.filter(video_id__id=videoID).values("kat_id__name")
    if not asString:
        cats_as_list = []
        for cat in cats:
            cats_as_list.append(cat["kat_id__name"])
        return cats_as_list
    else:
        cats_as_string = ""
        for i, cat in enumerate(cats):
            if i:
                cats_as_string += ", "
            cats_as_string += cat["kat_id__name"] + " "

        return cats_as_string


def generate_video_id():
    s = shortuuid.uuid()
    print(s)
    return s


def get_data_from_video_array(videos, asString=True):
    views = []
    tags = []
    for video in videos:
        views.append(get_watched_counter(video.id))
        tags.append(get_video_categories(video.id, asString=asString))

    return zip(videos, views, tags)

def user_activity(user):
    video_point = 5
    comment_point = 2
    points = 0
    points += len(Video.objects.filter(user=user)) * video_point
    points += len(Comment.objects.filter(user=user)) * comment_point
    return points
