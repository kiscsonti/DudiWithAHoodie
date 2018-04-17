from django import forms
from .models import Video
from django.core.exceptions import ValidationError


file_formats = ['MOV', 'MPEG4', 'MP4', 'AVI', 'WMV', 'MP3']
# TODO: delete MP3 from the file formats, it is only for testing

def validate_file_extension(value):
    extension = value.name.split()[-1].upper()
    if extension not in file_formats:
        raise ValidationError(u'Not supported extension' + extension + '. Please use ' + file_formats + ' format.')



class AddVideoForm(forms.Form):
    title = forms.CharField(max_length=500, required=True)
    categories = forms.CharField(max_length=150)
    file = forms.FileField(required=True, help_text='The video file', )
    is_commentable = forms.BooleanField(required=False, initial=True)

    def clean_file(self):
        filename = self.cleaned_data.get('file')
        extension = filename.name.split('.')[-1].upper()
        if extension not in file_formats:
            raise ValidationError(u'Not supported extension [' + extension + ']. Please use ' + str(file_formats) + ' format.')
        return filename

    class Meta:
        model = Video
        fields = ['title', 'categories', 'file', 'is_commentable', ]


class EditVideo(forms.Form):
    title = forms.CharField(max_length=100)
    is_commentable = forms.BooleanField(required=False)

    class Meta:
        model = Video
        fields = ['title', 'is_commentable', ]

