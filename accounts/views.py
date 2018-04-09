from django.shortcuts import render
from django.http import HttpResponse


def temp(request):
    html = "<html><body>Very niice</body></html>"
    return HttpResponse(html)
