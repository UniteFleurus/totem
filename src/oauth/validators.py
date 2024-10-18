import hashlib
import logging
from django.contrib.auth import get_user_model
from django.db.models.query import prefetch_related_objects
from oauth2_provider.models import get_access_token_model
from oauth2_provider.oauth2_validators import OAuth2Validator as BaseOAuth2Validator


AccessToken = get_access_token_model()
User = get_user_model()

_logger = logging.getLogger(__name__)


class OAuth2Validator(BaseOAuth2Validator):

    def _load_access_token(self, token):
        """ Override this as we don't want to select_related application field (useless for this
            service, for now). This is executed at each request, during auth phase. """
        token_checksum = hashlib.sha256(token.encode("utf-8")).hexdigest()
        return (
            AccessToken.objects.select_related("user")
            .filter(token_checksum=token_checksum)
            .first()
        )

    def validate_user(self, username, password, client, request, *args, **kwargs):
        result  = super().validate_user(username, password, client, request, *args, **kwargs)
        if result:
            # Prefetching user roles is needed to compute scopes to set on the token. They'll be put
            # in cache, otherwise each time a `user.roles.all()` is done, a query is executed.
            prefetch_related_objects([request.user], 'roles')
        return result
