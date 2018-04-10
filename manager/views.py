from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import datetime


now = datetime.datetime.now()

@login_required(redirect_field_name=None, login_url='/login')
def bejegyzes(request):
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)
