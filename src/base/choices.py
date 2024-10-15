from django.db import models


class FileReferencePrivacy(models.TextChoices):
    PUBLIC = 'public', 'Public'
    PRIVATE = 'private', 'Private'
