
from django.db import models


class UserType(models.TextChoices):
    PORTAL = "PORTAL", "Portal"
    INTERNAL = "INTERNAL", "Internal"
    ADMIN = "ADMIN", "Admin"
