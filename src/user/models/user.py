import os
import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager

from django.db import models

from base.files.storages import PrivateMediaFileSystemStorage
from base.models.mixins import CleanupFileQuerysetMixin, CleanupFileModelMixin
from user import choices


class UserManager(CleanupFileQuerysetMixin, BaseUserManager):
    pass


# ---------------------------------------------------------------
# User
# ---------------------------------------------------------------

def upload_to_user_avatar(instance, filename):
        file_name, file_extension = os.path.splitext(filename)
        return f"{instance._meta.app_label}.{instance.__class__.__name__}/{str(instance.pk)}/avatar{file_extension}"


class User(CleanupFileModelMixin, AbstractUser):
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, null=False, primary_key=True
    )
    username = models.CharField(
        "Username", max_length=255, null=False, blank=False)
    first_name = models.CharField(
        "First name", max_length=255, null=True, blank=True)
    last_name = models.CharField(
        "Last name", max_length=255, null=True, blank=True)
    email = models.EmailField("Email", max_length=255, null=False, blank=False)
    avatar = models.ImageField(storage=PrivateMediaFileSystemStorage(), upload_to=upload_to_user_avatar, max_length=256, null=True, blank=True)
    # preferences
    language = models.CharField(
        max_length=10, choices=settings.LANGUAGES, default='fr', null=False, blank=False
    )
    # access
    user_type = models.CharField(
        max_length=24,
        choices=choices.UserType.choices,
        default=choices.UserType.PORTAL,
        null=False,
        blank=False,
    )
    roles = models.ManyToManyField(
        'user.UserRole', related_name='users', through='UserRoleRelation'
    )

    objects = UserManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["username"],
                name="unique_username",
                violation_error_message="A user with that username already exists.",
            ),
        ]
