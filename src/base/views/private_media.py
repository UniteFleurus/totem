import os
from urllib.parse import urlparse

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse
from django.views.generic.base import View

from base.choices import FileReferencePrivacy
from base.models import FileReference
from core.utils import signing


class ServeSignedUrlsStorageNginxView(View):

    def dispatch(self, request, path, *args, **kwargs):
        is_ok = signing.check_signature(request.get_full_path())
        if not is_ok:
            raise PermissionDenied()
        return super().dispatch(request, path=path, *args, **kwargs)

    def get(self, request, path, *args, **kwargs):
        full_path = request.get_full_path()
        url_parsed = urlparse(full_path)

        file_path = url_parsed.path.replace(f"{settings.MEDIA_URL.rstrip('/')}/{FileReferencePrivacy.PRIVATE}/", '')
        try:
            file_reference = FileReference.objects.get(privacy=FileReferencePrivacy.PRIVATE, symbolic_path=file_path)
            x_redirect = os.path.join(settings.MEDIA_URL.rstrip('/'), '_filestore', file_reference.store_path.lstrip("/"))
            mimetype = file_reference.mimetype
        except ObjectDoesNotExist:
            raise Http404

        resp = HttpResponse()
        resp['X-Accel-Redirect'] = x_redirect
        resp['Content-Type'] = mimetype
        return resp
