from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Video, Category, VideoKategoria
from .forms import AddVideoForm
import datetime
import shortuuid

now = datetime.datetime.now()


@login_required(redirect_field_name=None, login_url='/login')
def bejegyzes(request):
    html = "<html><body>It is now %s.</body></html>" % now
    # TODO: If you want to visit a site that needs you to be logged in, it should redirect you back to where you were after logging in

    return render(request, 'index.html')


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
            return render(request, 'addvideo.html', {'form': form})


    else:
        form = AddVideoForm()

    return render(request, 'addvideo.html', {'form': form})


def show_video(request, videoID):
    video = Video.objects.get(id=videoID)
    return render(request, 'showvideo.html', {'videoObject': video})


def generate_video_id():
    s = shortuuid.uuid()
    print(s)
    return s


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
        posts = Post.objects.filter(id__in=templist)
        if len(posts) == 0:
            raise Http404("Nincs ilyen tag")
    else:
        return redirect('index')
    return render(request, 'htmls/index.html', {'posts': posts})
