import hashlib
import mimetypes
import os
import uuid
from django.db import models

from base import choices


class FileReference(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, null=False, primary_key=True
    )
    symbolic_path = models.CharField(
        "Symbolic Path", max_length=256, null=False, blank=False, help_text="Symbolic link from the Media Store to Filestore."
    )
    store_path = models.CharField(
        "Store Path", max_length=256, null=False, blank=False, help_text="Path in the Filestore."
    )
    checksum = models.CharField(
        "Checksum", max_length=256, null=False, blank=False, help_text="SHA1 of the binary data of the file."
    )
    mimetype = models.CharField("Mimetype", max_length=64, null=True, blank=True)
    privacy = models.CharField("Privacy", max_length=32, null=False, blank=False, choices=choices.FileReferencePrivacy.choices, help_text="Privacy means Media Store.")
    create_date = models.DateTimeField("Create Date", auto_now_add=True)

    class Meta:
        verbose_name = "File Reference"
        verbose_name_plural = "File References"
        constraints = [
            models.UniqueConstraint(
                fields=["privacy", "symbolic_path"],
                name="unique_symlink_privacy",
                violation_error_message="Only one symlink in the privacy store.",
            ),
        ]

    @classmethod
    def precompute_values(cls, bin_data, upload_to_path):
        checksum = hashlib.sha1(bin_data or b'').hexdigest()
        mimetype = mimetypes.guess_type(upload_to_path)[0]
        store_path = os.path.join(checksum[:2], checksum)

        return {
            'store_path': store_path,
            'checksum': checksum,
            'mimetype': mimetype,
        }
