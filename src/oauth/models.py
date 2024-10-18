import uuid

from django.db import models
from django.db.models import Q, Subquery
from oauth2_provider.models import (
    AbstractAccessToken,
    AbstractApplication,
    AbstractGrant,
    AbstractIDToken,
    AbstractRefreshToken,
)


class OAuthApp(AbstractApplication):
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, null=False, primary_key=True
    )

    class Meta:
        verbose_name = "OAuth Application"
        verbose_name_plural = "OAuth Applications"


class RefreshToken(AbstractRefreshToken):
    pass


class Grant(AbstractGrant):
    pass


class IDToken(AbstractIDToken):
    pass


# ------------------------------------------------
# Access Token
# ------------------------------------------------


class AccessTokenQuerySet(models.QuerySet):

    def invalidate_user_token(self, user_qs):
        """Delete user token for given users since their rights have changed. It only have
        to remove the token that were automatically generated. We consider only tokens
        with an application of `password-based` flow, or not linked to an application (SSO flow).
        :params user_qs : user queryset for which tokens need to be dropped
        """
        return self.filter(
            Q(user_id__in=Subquery(user_qs.values_list('pk')))
            & (
                Q(
                    application__authorization_grant_type__in=[
                        OAuthApp.GRANT_PASSWORD
                    ]
                )
                | Q(application__isnull=True)
            )
        ).delete()


class AccessToken(AbstractAccessToken):
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, null=False, primary_key=True
    )

    objects = AccessTokenQuerySet.as_manager()
