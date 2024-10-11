import re
from django.conf import settings
from django.urls import re_path

from . import views

print('==============settings.MEDIA_ROOT',settings.MEDIA_ROOT)
urlpatterns = [
    re_path(
        r'^%s(?P<path>.*)$' % re.escape(
            settings.MEDIA_URL.lstrip('/')
        ),
        views.ServeSignedUrlsStorageNginxView.as_view()
    ),
]
