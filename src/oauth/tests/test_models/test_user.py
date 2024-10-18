from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from oauth.models import AccessToken, OAuthApp
from user.models import UserRole, User, UserRoleRelation
from user import choices


class UserChangeRightTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.role_a, cls.role_b = UserRole.objects.bulk_create([
            UserRole(id="TEST1_OFFICER", name="Role 1"),
            UserRole(id="TEST2_OFFICER", name="Role 2"),
        ])

        cls.user = User.objects.create(
            username="han@solo.com",
            email="han@solo.com",
            user_type=choices.UserType.INTERNAL,
        )
        cls.user_role_rel_a = UserRoleRelation.objects.create(
            user=cls.user,
            role=cls.role_a,
        )

        # oauth app
        cls.oauth_app = OAuthApp.objects.create(
            name="Application Simulating Frontend",
            client_type=OAuthApp.CLIENT_PUBLIC,
            authorization_grant_type=OAuthApp.GRANT_CLIENT_CREDENTIALS,
            redirect_uris="",  # value when creation through django DOT form on /o/applications/
            skip_authorization=False,
        )
        cls.oauth_app_password = OAuthApp.objects.create(
            name="Application Simulating Other Client",
            client_type=OAuthApp.CLIENT_PUBLIC,
            authorization_grant_type=OAuthApp.GRANT_PASSWORD,
            redirect_uris="",  # value when creation through django DOT form on /o/applications/
            skip_authorization=False,
        )

        # tokens
        cls.token1 = AccessToken.objects.create(
            token="secure_user_token",
            scope="test.notification.send",
            user=cls.user,
            application=cls.oauth_app,
            expires=timezone.now() + timedelta(days=365),
        )
        cls.token2 = AccessToken.objects.create(
            token="secure_user_token2",
            scope="test.notification.send",
            user=cls.user,
            application=cls.oauth_app_password,
            expires=timezone.now() + timedelta(days=365),
        )
        cls.token3 = AccessToken.objects.create(
            token="secure_user_token3",
            scope="test.notification.send",
            user=cls.user,
            application=None,  # no app
            expires=timezone.now() + timedelta(days=365),
        )

    def test_change_other_field(self):
        self.user.email = "thisis@test.com"
        self.user.save(update_fields=["email"])

        self.assertTrue(AccessToken.objects.filter(pk=self.token1.pk).exists())
        self.assertTrue(AccessToken.objects.filter(pk=self.token2.pk).exists())
        self.assertTrue(AccessToken.objects.filter(pk=self.token3.pk).exists())

    def test_change_user_type(self):
        self.user.user_type = choices.UserType.ADMIN
        self.user.save(update_fields=["user_type"])

        self.assertTrue(AccessToken.objects.filter(pk=self.token1.pk).exists())
        self.assertFalse(AccessToken.objects.filter(pk=self.token2.pk).exists())
        self.assertFalse(AccessToken.objects.filter(pk=self.token3.pk).exists())

    def test_add_role_relation(self):
        UserRoleRelation.objects.create(
            user=self.user,
            role=self.role_b,
        )

        self.assertTrue(AccessToken.objects.filter(pk=self.token1.pk).exists())
        self.assertFalse(AccessToken.objects.filter(pk=self.token2.pk).exists())
        self.assertFalse(AccessToken.objects.filter(pk=self.token3.pk).exists())

    def test_delete_role_relation(self):
        self.user_role_rel_a.delete()

        self.assertTrue(AccessToken.objects.filter(pk=self.token1.pk).exists())
        self.assertFalse(AccessToken.objects.filter(pk=self.token2.pk).exists())
        self.assertFalse(AccessToken.objects.filter(pk=self.token3.pk).exists())

    def test_change_role_relation(self):
        self.user_role_rel_a.role = self.role_b
        self.user_role_rel_a.save()

        self.assertTrue(AccessToken.objects.filter(pk=self.token1.pk).exists())
        self.assertFalse(AccessToken.objects.filter(pk=self.token2.pk).exists())
        self.assertFalse(AccessToken.objects.filter(pk=self.token3.pk).exists())
