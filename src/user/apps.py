from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class UserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "user"

    def ready(self):
        autodiscover_modules('permissions')

    populate_fixtures = ["user_role", "user"]
