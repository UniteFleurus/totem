import re
from django.conf import settings
from django.urls import re_path

from . import views

urlpatterns = [
    # media/private
    re_path(
        r'^%s(?P<path>.*)$' % re.escape(
            settings.MEDIA_URL.lstrip('/')
        ),
        views.ServeSignedUrlsStorageNginxView.as_view()
    ),
]
