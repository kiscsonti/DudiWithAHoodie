from django import forms
from .models import Video
from django.core.exceptions import ValidationError
from .models import Playlist


file_formats = ['MOV', 'MPEG4', 'MP4', 'AVI', 'WMV', ]
image_formats = ['JPG', 'PNG']
# TODO: delete MP3 from the file formats, it is only for testing

def validate_file_extension(value):
    extension = value.name.split(".")[-1].upper()
    if extension not in file_formats:
        raise ValidationError(u'Not supported extension' + extension + '. Please use ' + str(file_formats) + ' format.')


def validate_image_extension(value):
    extension = value.name.split(".")[-1].upper()
    #print("extension: ", extension)
    #print("all of it: ", value.name.split())
    if extension not in image_formats:
        raise ValidationError(u'Not supported extension' + extension + '. Please use ' + str(image_formats) + ' format.')


class AddVideoForm(forms.Form):
    title = forms.CharField(max_length=500, required=True, help_text="Videó címe")
    categories = forms.CharField(max_length=150, help_text="Milyen kategóriákba tartozik a videó")
    file = forms.FileField(required=True, help_text='A videó fájl', validators=[validate_file_extension])
    thumbnail = forms.ImageField(help_text="Kép amit más felhasználók látnak a videóra kattintás előtt",
                                 required=False,
                                 validators=[validate_image_extension])
    description = forms.CharField(max_length=500, required=False, help_text="Video leírása")
    is_commentable = forms.BooleanField(required=False, initial=True, help_text="Kommentelhetőség")

    def clean_file(self):
        filename = self.cleaned_data.get('file')
        extension = filename.name.split('.')[-1].upper()
        if extension not in file_formats:
            raise ValidationError(u'Not supported extension [' + extension + ']. Please use ' + str(file_formats) + ' format.')
        return filename

    class Meta:
        model = Video
        fields = ['title', 'categories', 'file', 'description', 'thumbnail', 'is_commentable', ]


class EditVideo(forms.Form):
    title = forms.CharField(max_length=100)
    description = forms.CharField(max_length=500, required=False, help_text="Video leírása")
    is_commentable = forms.BooleanField(required=False)

    class Meta:
        model = Video
        fields = ['title', 'is_commentable', 'description', ]


class CreatePlaylist(forms.Form):
    title = forms.CharField(max_length=100, help_text="Lejátszási lista címe", required=True, )

    class Meta:
        model = Video
        fields = ['title', ]

class AddToPlaylist(forms.Form):
    playlists = forms.ChoiceField(widget=forms.Select(), required=True, )


    def __init__(self, user, *args, **kwargs):
        super(AddToPlaylist, self).__init__(*args, **kwargs)
        self.fields['playlists'] = forms.ChoiceField(choices=self.get_user_playlistnames(user), required=True)

    class Meta:
        model = Video
        fields = ['playlists', ]

    def get_user_playlistnames(self, user):
        playlists = Playlist.objects.filter(user=user)
        names = [(plist.id, plist.title) for plist in playlists]
        return names
