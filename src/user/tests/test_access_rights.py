from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from parameterized import parameterized

from user.access_rights import get_all_permission, register_permission


class TestAccessRightsTest(TestCase):

    @parameterized.expand(
        [
            ("totem.mymodel.action", True),
            ("#sml", False),
            ("this.will.be.too.long", False),
            ("aa.bbc.cccc", False),
            ("123456", False),
            ("user.view_user", False),
        ]
    )
    def test_permission_regex(self, perm, is_valid):
        if is_valid:
            register_permission(perm, "a description", is_public=False)
            self.assertIn(perm, dict(get_all_permission()))
        else:
            with self.assertRaises(
                ImproperlyConfigured
            ):
                register_permission(perm, "a description", is_public=False)
