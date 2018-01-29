from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. This will be the Events Manager.")
