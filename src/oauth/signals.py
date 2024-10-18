from django.apps import apps
from django.dispatch import receiver

from user import signals


@receiver(signals.user_change_rights)
def user_change_role_handler(sender, **kwargs):
    AccessToken = apps.get_model("oauth", "AccessToken")
    AccessToken.objects.invalidate_user_token(kwargs.get("user_qs", []))
