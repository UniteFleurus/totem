
from django.db import models


class UserType(models.TextChoices):
    PORTAL = "PORTAL", "Portal"
    INTERNAL = "INTERNAL", "Internal"
    ADMIN = "ADMIN", "Admin"


class UserRole(models.TextChoices):
    SCOUT_CHIEF = "SCOUT_CHIEF", "Chief"
    SCOUT_LEADER_CHIEF = "SCOUT_LEADER", "Leader Chief"
    SCOUT_GROUP_CHIEF = "SCOUT_GROUP_CHIEF", "Group Chief"
