from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Video, Category, VideoKategoria, Watched, Comment, Playlist
from .forms import AddVideoForm, EditVideo
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.db.models import Count
from django.utils import timezone
import shortuuid

now = datetime.now()


@login_required(redirect_field_name=None, login_url='/login')
def index(request):
    html = "<html><body>It is now %s.</body></html>" % now
    # TODO: If you want to visit a site that needs you to be logged in, it should redirect you back to where you were after logging in


    video_list = Video.objects.order_by('create_date', 'create_time').reverse()
    page = request.GET.get('page', 1)
    paginator = Paginator(video_list, 5)
    try:
        videos = paginator.page(page)
    except PageNotAnInteger:
        videos = paginator.page(1)
    except EmptyPage:
        videos = paginator.page(paginator.num_pages)

    combined = get_data_from_video_array(videos)

    return render(request, 'index.html', {'videos': combined})


def hot(request):
    html = "<html><body>It is now %s.</body></html>" % now
    # TODO: If you want to visit a site that needs you to be logged in, it should redirect you back to where you were after logging in
    if request.GET.get("Date"):
        date = request.GET.get("Date")

        how_many_days = get_days(date)
        if how_many_days == -1:
            #All ág
            video_list = Watched.objects.all()\
                .values('video_id')\
                .annotate(total=Count('video_id'))\
                .order_by('total')
        else:
            #Minden más ág (DAY, MONTH, YEAR)
            time_threshold = timezone.now() - timedelta(days=how_many_days)
            video_list = Watched.objects.filter(watched_date__gte=time_threshold)\
                .values('video_id')\
                .annotate(total=Count('video_id'))\
                .order_by('total')
    else:
        video_list = Watched.objects.all()\
            .values('video_id')\
            .annotate(total=Count('video_id'))\
            .order_by('total')
    page = request.GET.get('page', 1)
    paginator = Paginator(video_list, 5)
    try:
        videos = paginator.page(page)
    except PageNotAnInteger:
        videos = paginator.page(1)
    except EmptyPage:
        videos = paginator.page(paginator.num_pages)

    all_video_ids = [vidi['video_id']for vidi in videos]
    print(all_video_ids)
    combined = get_data_from_video_array(all_video_ids, isIDs=True)
    for a, b, c in combined:
        pass
    #TODO: something is buggy here
    return render(request, 'hot.html', {'videos': combined})


@login_required
def add_video(request):
    if request.method == 'POST':
        form = AddVideoForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            file = form.cleaned_data.get('file')
            commentable = form.cleaned_data.get('is_commentable')
            video = Video(id=generate_video_id(),
                          user=request.user,
                          title=title,
                          filename=file,
                          is_commentable=commentable)
            video.save()

            categories = str(form.cleaned_data.get('categories')).split(' ')
            for cat in categories:

                if not Category.objects.filter(name=cat).exists():
                    cat = Category(name=cat)
                    cat.save()

                connection = VideoKategoria(video_id=video, kat_id=Category.objects.filter(name=cat).first())
                connection.save()

            return redirect('video', videoID=video.id)
    else:
        form = AddVideoForm()

    return render(request, 'addvideo.html', {'form': form})


def show_video(request, videoID):
    # TODO: Make the video appear nice, and make it controllable

    video = Video.objects.get(id=videoID)
    owner = video.user
    viewCount = get_watched_counter(videoID)
    owned = (owner == request.user)
    if request.method == 'POST':

        if (request.POST.get("del")):
            Comment.objects.get(id=request.POST.get("del")).delete()

        else:
            text = request.POST.get("comment")
            if len(text) > 0:
                text = text.replace("\r\n", "<br/>")
                comment = Comment(user=request.user, content=text, video_id=video)
                comment.save()

    comments = Comment.objects.filter(video_id=videoID).order_by('create_date', 'create_time').reverse()

    return render(request, 'showvideo.html', {'videoObject': video, 'owner': owner, 'viewCount': viewCount, 'owned': owned, 'comments': comments})


def search(request):
    query = request.GET.get('q')
    help = []
    if query and query != '':
        splitted = query.split(' ')
        for item in splitted:
            if str(item).startswith('#'):
                item = item[1:]
            help.extend(list(VideoKategoria.objects.filter(kat_id__name__contains=item).values('video_id__id')))

            # help = TagToMeme.objects.filter(toTag__name__contains__in=splitted).values('toPost__id')
            # posts = Post.objects.filter(id=help)

        templist = list()
        for it in help:
            templist.append(it['toPost__id'])
        posts = Video.objects.filter(id__in=templist)
        if len(posts) == 0:
            raise Http404("Nincs ilyen tag")
    else:
        return redirect('index')
    return render(request, 'index.html', {'posts': posts})


def watched(request, videoID, userID):
    user = User.objects.get(id=userID)
    video = Video.objects.get(id=videoID)
    watchedvideo = Watched(user=user, video_id=video)
    print('That\'s right')
    watchedvideo.save()

    owner = video.user
    viewCount = Watched.objects.filter(video_id=videoID).count()
    owned = (owner == request.user)
    return redirect('video', videoID=videoID)


def edit_video(request, videoID):
    owner = Video.objects.get(id=videoID).user
    if request.user != owner:
        raise PermissionDenied

    if request.method == 'POST':

        if 'modify' in request.POST:

            form = EditVideo(request.POST)
            if form.is_valid():

                video = Video.objects.get(pk=videoID)
                video.title = form.cleaned_data.get('title')
                video.is_commentable = form.cleaned_data.get('is_commentable')
                video.save()

                return redirect('video', videoID=video.id)
        else:
            video = Video.objects.get(pk=videoID)
            video.delete()
            return redirect('profile', user_id=owner.id)
    else:

        video = Video.objects.get(pk=videoID)
        form = EditVideo(initial={'title': video.title, 'is_commentable': video.is_commentable})

    return render(request, 'editvideo.html', {'form': form})

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def watched_video(request):
    video = request.GET.get('video', None)
    user = request.GET.get('user', None)
    print(user)
    video = Video.objects.get(id=video)
    user = User.objects.get(id=user)
    new_watched_video = Watched(video=video, user=user)
    new_watched_video.save()
    data = {
        'is_taken': True
    }
    return JsonResponse(data)


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


def get_data_from_video_array(videos, asString=True, isIDs=False):

    views = []
    tags = []
    for video in videos:
        print(video)
        if isIDs:
            views.append(get_watched_counter(video))
            tags.append(get_video_categories(video, asString=asString))
        else:
            views.append(get_watched_counter(video.id))
            tags.append(get_video_categories(video.id, asString=asString))

    return zip(videos, views, tags)


def get_days(date):
    if date == "Day":
        return 1
    elif date == "Month":
        return 30
    elif date == "Year":
        return 365
    else:
        return -1
