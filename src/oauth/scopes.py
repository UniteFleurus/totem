from oauth2_provider.scopes import BaseScopes

from user.access_rights import get_all_permission


class TotemScopes(BaseScopes):

    def get_all_scopes(self):
        return dict(get_all_permission())

    def get_available_scopes(self, application=None, request=None, *args, **kwargs):
        """This returns the same available scopes for every application/request.
        This must be a subset of `get_all_scopes`, and returns a list with scopes.
        """
        return list(self.get_all_scopes())

    def get_default_scopes(self, application=None, request=None, *args, **kwargs): # noqa
        # return the token of the user, since no scope was asked in initial request
        if request.user and not request.scopes:
            return self.get_user_scopes(request.user)
        return []

    def get_user_scopes(self, user):
        scopes = set()
        for role in user.roles.all():
            scopes |= set(role.permissions or [])
        return list(scopes)
