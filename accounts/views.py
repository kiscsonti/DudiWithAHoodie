from django.http import HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from manager.models import Video, Playlist

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
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def profile(request, user_id):
    user = User.objects.get(username=user_id)
    videos = Video.objects.filter(user=user)
    playlists = Playlist.objects.filter(user=user)
    return render(request, 'profile.html', {'profile': user, 'videos': videos, 'playlists': playlists})