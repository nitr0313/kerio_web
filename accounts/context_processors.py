from django.conf import settings


def current_version(request):
    return {"current_version": settings.VERSION}
