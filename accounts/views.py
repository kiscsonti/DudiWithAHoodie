from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from manager.models import Video, Playlist
from manager.views import get_watched_counter, get_video_categories
from manager.utils import user_activity
from django.contrib.auth.decorators import login_required

def temp(request):
    html = "<html><body>Very niice</body></html>"
    return HttpResponse(html)



def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


@login_required(redirect_field_name="/", login_url='/login')
def profile(request, user_id):
    user = User.objects.get(username=user_id)
    videos = Video.objects.filter(user=user)
    views = []
    tags = []
    for video in videos:
        views.append(get_watched_counter(video.id))
        tags.append(get_video_categories(video.id, asString=True))

    combined = zip(videos, views, tags)
    playlists = Playlist.objects.filter(user__username=user)
    print(playlists)
    return render(request, 'profile.html', {'profile': user, 'videos': combined, 'playlists': playlists})


@login_required(redirect_field_name="/", login_url='/login')
def most_active(request):
    max_val = 0
    max_usr = None
    for usr in User.objects.all():
        tmp = user_activity(usr)
        if max_val < tmp:
            max_val = tmp
            max_usr = usr

    return redirect('profile', user_id=max_usr.username)
