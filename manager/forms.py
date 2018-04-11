from django import forms
from .models import Video


class AddVideoForm(forms.Form):
    title = forms.CharField(max_length=500, required=True)
    categories = forms.CharField(max_length=150)
    file = forms.FileField(required=True, help_text='The video file', )
    is_commentable = forms.BooleanField()

    class Meta:
        model = Video
        fields = ['title', 'categories', 'image', 'is_commentable', ]
