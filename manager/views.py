from django.shortcuts import render
from django.http import HttpResponse
import datetime

now = datetime.datetime.now()


def bejegyzes(request):
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)
