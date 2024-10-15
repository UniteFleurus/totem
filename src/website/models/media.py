import uuid
import hashlib
import mimetypes
from django.db import models

from base.files.storages import PublicMediaFileSystemStorage
from base.models.mixins import CleanupFileQuerysetMixin, CleanupFileModelMixin


class MediaQuerySet(CleanupFileQuerysetMixin, models.QuerySet):
    pass


class Media(CleanupFileModelMixin, models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, null=False, primary_key=True
    )
    name = models.CharField(
        "Name", max_length=256, null=False, blank=False, help_text="Path in the filestore"
    )
    content = models.FileField(
        storage=PublicMediaFileSystemStorage(),
        upload_to="website/%Y/%m",
        null=False,
        max_length=256,
        blank=False,
    )
    checksum = models.CharField(
        "Checksum", max_length=128, null=False, blank=False, help_text="SHA1 of the binary data of the file"
    )
    mimetype = models.CharField("Mimetype", max_length=64, null=True, blank=True)
    create_date = models.DateTimeField("Create Date", auto_now_add=True)

    objects = MediaQuerySet.as_manager()

    class Meta:
        verbose_name = "Media"
        verbose_name_plural = "Medias"

    @classmethod
    def precompute_values(cls, bin_data, filename=None):
        checksum = hashlib.sha1(bin_data or b'').hexdigest()
        mimetype = mimetypes.guess_type(filename)[0] if filename else None
        return {
            'checksum': checksum,
            'mimetype': mimetype,
            'name': filename,
        }
