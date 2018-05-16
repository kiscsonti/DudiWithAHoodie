from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Video, Category, VideoKategoria, Watched, Comment, Playlist, ListVideos
from .forms import AddVideoForm, EditVideo, CreatePlaylist, AddToPlaylist
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.db.models import Count
from django.utils import timezone
from .utils import get_after_date, get_data_from_video_ids, get_days, get_video_categories, get_watched_counter, \
    generate_video_id, get_data_from_video_array, recently_watched, count_category, get_not_watched_videos
import shortuuid
import json

now = datetime.now()


@login_required(redirect_field_name="/", login_url='/login')
def index(request):
    # TODO: If you want to visit a site that needs you to be logged in, it should redirect you back to where you were after logging in


    video_list = Video.objects.order_by('create_datetime').reverse()
    page = request.GET.get('page', 1)
    paginator = Paginator(video_list, 5)
    try:
        videos = paginator.page(page)
    except PageNotAnInteger:
        videos = paginator.page(1)
    except EmptyPage:
        videos = paginator.page(paginator.num_pages)

    combined = get_data_from_video_array(videos)

    return render(request, 'index.html', {'videos': combined, "pagi": videos})


@login_required(redirect_field_name="/hot", login_url='/login')
def hot(request):
    # TODO: If you want to visit a site that needs you to be logged in, it should redirect you back to where you were after logging in
    if request.GET.get("Date"):
        date = request.GET.get("Date")

        how_many_days = get_days(date)
        if how_many_days == -1:
            # All ág
            # TODO: SQL command
            video_list = Watched.objects.all() \
                .values('video_id') \
                .annotate(total=Count('video_id')) \
                .order_by('total').reverse()
        else:
            # Minden más ág (DAY, MONTH, YEAR)
            # TODO: SQL command
            time_threshold = timezone.now() - timedelta(days=how_many_days)
            video_list = Watched.objects.filter(watched_date__gte=time_threshold) \
                .values('video_id') \
                .annotate(total=Count('video_id')) \
                .order_by('total').reverse()
    else:
        # TODO: SQL command
        video_list = Watched.objects.all() \
            .values('video_id') \
            .annotate(total=Count('video_id')) \
            .order_by('total').reverse()
    page = request.GET.get('page', 1)
    paginator = Paginator(video_list, 5)
    try:
        videos = paginator.page(page)
    except PageNotAnInteger:
        videos = paginator.page(1)
    except EmptyPage:
        videos = paginator.page(paginator.num_pages)

    all_video_ids = [vidi['video_id'] for vidi in videos]
    combined = get_data_from_video_ids(all_video_ids)
    # TODO: something is buggy here
    return render(request, 'hot.html', {'videos': combined, "pagi": videos})


@login_required(redirect_field_name="/add", login_url='/login')
def add_video(request):
    if request.method == 'POST':
        form = AddVideoForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            file = form.cleaned_data.get('file')
            leiras = form.cleaned_data.get('description')
            thumbnail = form.cleaned_data.get('thumbnail')
            commentable = form.cleaned_data.get('is_commentable')
            video = Video(id=generate_video_id(),
                          user=request.user,
                          title=title,
                          filename=file,
                          description=leiras,
                          thumbnail=thumbnail,
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


# TODO: vigyen vissza a video oldalára
@login_required(redirect_field_name=None, login_url='/login')
def show_video(request, videoID):
    # TODO: Make the video appear nice, and make it controllable

    video = Video.objects.get(id=videoID)
    owner = video.user
    if owner == None:
        owner = "deleted user"
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

    comments = Comment.objects.filter(video_id=videoID).order_by('create_datetime').reverse()

    return render(request, 'showvideo.html',
                  {'videoObject': video, 'owner': owner, 'viewCount': viewCount, 'owned': owned, 'comments': comments})


# TODO: keresés működjön minden opcióra
def search2(request):
    query = request.GET.get('q')
    date = request.GET.get('Date')
    type = request.GET.get('Type')

    if date is None:
        date = "All"
    if type is None:
        type = "Category"

    is_user = False
    items = []
    if query and query != '':

        if type == "User":
            is_user = True
            items = User.objects.filter(username__contains=query)
        elif type == "Category":
            items = VideoKategoria.objects.filter(kat_id__name__contains=query).values("video_id__id")
            items = [vidi['video_id__id'] for vidi in items]

        elif type == "Title":
            items = Video.objects.filter(title__contains=query).values("id")
            items = [vidi['id'] for vidi in items]

        else:
            pass

        if type != "User":
            how_many_days = get_days(date)
            items = get_after_date(items, how_many_days)


    else:
        return redirect('index')
    return render(request, 'search.html', {'searched': query,
                                           'is_user': is_user,
                                           'items': items,
                                           'type': type,
                                           'date': date})


# TODO: menjen vissza a videó oldalára login után
@login_required(redirect_field_name=None, login_url='/login')
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
                video.description = form.cleaned_data.get('description')
                video.is_commentable = form.cleaned_data.get('is_commentable')
                video.save()

                return redirect('video', videoID=video.id)
        else:
            video = Video.objects.get(pk=videoID)
            video.delete()
            return redirect('profile', user_id=owner.id)
    else:

        video = Video.objects.get(pk=videoID)
        form = EditVideo(
            initial={'title': video.title, 'description': video.description, 'is_commentable': video.is_commentable})

    return render(request, 'editvideo.html', {'form': form})


@login_required(redirect_field_name="/", login_url='/login')
def create_playlist(request):
    if request.method == 'POST':
        form = CreatePlaylist(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            playlist = Playlist(title=title, user=request.user)
            playlist.save()
            return redirect('index', )
    else:
        form = CreatePlaylist()

    return render(request, 'create_playlist.html', {'form': form})


@login_required(redirect_field_name="/", login_url='/login')
def add_to_playlist(request):
    video = request.GET.get('video')
    video = Video.objects.get(id=video)
    if video == None:
        raise Http404("A kért videó nem létezik")
    if request.method == 'POST':
        form = AddToPlaylist(request.user, request.POST, )
        if form.is_valid():
            playlist = form.cleaned_data.get('playlists')
            playlist = Playlist.objects.get(id=playlist)

            listavideo = ListVideos(list_id=playlist, video_id=video,
                                    sorszam=(len(ListVideos.objects.filter(list_id=playlist)) + 1))

            listavideo.save()
            return redirect('index', )
    else:
        form = AddToPlaylist(request.user)

    return render(request, 'add_to_playlist.html', {'form': form})

    pass


@login_required(redirect_field_name="/", login_url='/login')
def play_playlist(request, playlist_id, id):
    pass


@login_required(redirect_field_name="/", login_url='/login')
def similiar(request):
    watched_ = recently_watched(request.user)
    szotar = count_category(watched_)
    szotar = sorted(szotar.items(), key=lambda x: x[1], reverse=True)
    # szotar = sorted(szotar, key=szotar.get)
    most_freq = 3
    search_categories_list = [item[0] for item in szotar[:most_freq]]
    print(search_categories_list)

    if len(search_categories_list) == 0:
        return render(request, 'index.html')
    video_list = get_not_watched_videos(request.user, search_categories_list)
    page = request.GET.get('page', 1)
    paginator = Paginator(video_list, 5)
    try:
        videos = paginator.page(page)
    except PageNotAnInteger:
        videos = paginator.page(1)
    except EmptyPage:
        videos = paginator.page(paginator.num_pages)

    combined = get_data_from_video_array(videos)
    return render(request, 'index.html', {'videos': combined, "pagi": videos})


@csrf_exempt
def watched_video(request):
    if request.method == 'POST':
        usr = request.POST.get('user')
        vid = request.POST.get('video')
        print(usr, vid)
        response_data = {}
        usr = User.objects.get(username=usr)
        vid = Video.objects.get(id=vid)

        w = Watched(user=usr, video_id=vid)
        w.save()

        response_data['result'] = 'Create post successful!'
        response_data['postpk'] = usr.pk

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )


"""video = request.GET.get('video', None)
    user = request.GET.get('user', None)
    print(user)
    video = Video.objects.get(id=video)
    user = User.objects.get(id=user)
    new_watched_video = Watched(video=video, user=user)
    new_watched_video.save()
    data = {
        'is_taken': True
    }
    return JsonResponse(data)"""

"""
def filter_olds(videos):
    vidis = []
    for video in videos:
        v = Video.objects.get(id=video)
"""
"""
# TODO: ez nem kell a jelenlegi verzióba
def watched(request, videoID, userID):
    user = User.objects.get(id=userID)
    video = Video.objects.get(id=videoID)
    watchedvideo = Watched(user=user, video_id=video)
    print('Thats right')
    watchedvideo.save()

    owner = video.user
    viewCount = Watched.objects.filter(video_id=videoID).count()
    owned = (owner == request.user)
    return redirect('video', videoID=videoID)
"""

"""
def search(request):
    query = request.GET.get('q')
    video_set = set()
    user_set = set()
    if query and query != '':
        splitted = query.split(' ')
        for item in splitted:
            video_set.union(list(VideoKategoria.objects.filter(kat_id__name__contains=item).values('video_id__id')))
            video_set.union(list(Video.objects.filter(title__contains=item).values('id')))
            user_set.union(list(User.objects.filter(username__contains=item)))

            # video_set = TagToMeme.objects.filter(toTag__name__contains__in=splitted).values('toPost__id')
            # posts = Post.objects.filter(id=video_set)

        if len(video_set) == 0 and len(user_set) == 0:
            raise Http404("Nincs ilyen felhasználó, se videó, se kategória")
        else:
            videos = []
            for id in video_set:
                videos.append(Video.objects.get(id=id))
    else:
        return redirect('index')
    return render(request, 'index.html', {'videos': videos, 'users': user_set, 'searched': query,})
"""
