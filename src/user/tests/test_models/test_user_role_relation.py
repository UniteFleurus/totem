from unittest.mock import patch
from django.test import TestCase

from user.models import User, UserRole, UserRoleRelation

USER_ID1 = "14041cce-8719-4637-92b1-51c4ade4b643"
USER_ID2 = "25f50950-7228-4f40-a68f-3aafdb4e1b67"
USER_ID3 = "3d9afc04-8ac2-40be-83de-a3c3e171923c"


class TestUserRoleRelationModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = User.objects.create(
            pk=USER_ID1,
            username="Tintin",
            password="MiL0u4ev3r",
            email="tintin@moulinsart.com",
        )
        cls.user_2 = User.objects.create(
            pk=USER_ID2,
            username="Haddock",
            password="MilleMilliardDeMillesabords",
            email="capitain@moulinsart.com",
        )
        cls.user_3 = User.objects.create(
            pk=USER_ID3,
            username="proftournesol",
            password="ObjectIfLuN3",
            email="trifon@moulinsart.com",
        )

        cls.role_a, cls.role_b = UserRole.objects.bulk_create([
            UserRole(id="TEST_ROLE1", name="Role 1"),
            UserRole(id="TEST_ROLE2", name="Role 2"),
        ])

        cls.user_role_rel_1a = UserRoleRelation.objects.create(
            user=cls.user_1,
            role=cls.role_a,
        )
        cls.user_role_rel_2a = UserRoleRelation.objects.create(
            user=cls.user_2,
            role=cls.role_a,
        )

    # ------------------------------------------
    # Tests signals
    # ------------------------------------------

    @patch('user.signals.user_change_rights.send')
    def test_signal_instance_create(
        self, mock
    ):
        def side_effect_assert(sender=None, user_qs=None):
            ids = [str(pk) for pk in user_qs.values_list('id', flat=True)]
            self.assertEqual([USER_ID3], ids)

        mock.side_effect = side_effect_assert

        rel = UserRoleRelation(user=self.user_3, role=self.role_b)
        rel.save()

        self.assertEqual(mock.call_count, 1)

    @patch('user.signals.user_change_rights.send')
    def test_signal_instance_update(
        self, mock
    ):
        def side_effect_assert(sender=None, user_qs=None):
            ids = [str(pk) for pk in user_qs.values_list('id', flat=True)]
            self.assertEqual([USER_ID1], ids)

        mock.side_effect = side_effect_assert

        self.user_role_rel_1a.role = self.role_b
        self.user_role_rel_1a.save(update_fields=['role'])

        self.assertEqual(mock.call_count, 1)

    @patch('user.signals.user_change_rights.send')
    def test_signal_instance_delete(
        self, mock
    ):
        def side_effect_assert(sender=None, user_qs=None):
            ids = [str(pk) for pk in user_qs.values_list('id', flat=True)]
            self.assertEqual([USER_ID1], ids)

        mock.side_effect = side_effect_assert

        self.user_role_rel_1a.delete()

        self.assertEqual(mock.call_count, 1)

    @patch('user.signals.user_change_rights.send')
    def test_signal_queryset_create(
        self, mock
    ):
        def side_effect_assert(sender=None, user_qs=None):
            ids = [str(pk) for pk in user_qs.values_list('id', flat=True)]
            self.assertEqual([USER_ID3], ids)

        rel = UserRoleRelation(user=self.user_3, role=self.role_a)
        UserRoleRelation.objects.bulk_create([rel])

        self.assertEqual(mock.call_count, 1)

    @patch('user.signals.user_change_rights.send')
    def test_signal_queryset_update(
        self, mock
    ):
        def side_effect_assert(sender=None, user_qs=None):
            ids = [str(pk) for pk in user_qs.values_list('id', flat=True)]
            self.assertEqual([USER_ID1, USER_ID2], ids)

        mock.side_effect = side_effect_assert

        rels = UserRoleRelation.objects.filter(pk__in=[self.user_role_rel_1a.pk, self.user_role_rel_2a.pk])
        rels.update(role=self.role_b)

        self.assertEqual(mock.call_count, 1)

    @patch('user.signals.user_change_rights.send')
    def test_signal_queryset_delete(
        self, mock
    ):
        def side_effect_assert(sender=None, user_qs=None):
            ids = [str(pk) for pk in user_qs.values_list('id', flat=True)]
            self.assertEqual([USER_ID1, USER_ID2], ids)

        mock.side_effect = side_effect_assert

        rels = UserRoleRelation.objects.filter(pk__in=[self.user_role_rel_1a.pk, self.user_role_rel_2a.pk])
        rels.delete()

        self.assertEqual(mock.call_count, 1)
