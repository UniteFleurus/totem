from asgiref.sync import async_to_sync
from collections import namedtuple
from django.db.models import Q
from django.test import TestCase
from parameterized import parameterized

from user.models import User, UserRole
from user.access_policy import apply_access_rules_sync, access_policy, BaseRule, ALL_ACTIONS


USER_ID1 = "14041cce-8719-4637-92b1-51c4ade4b643"
USER_ID2 = "25f50950-7228-4f40-a68f-3aafdb4e1b67"
USER_ID3 = "3d9afc04-8ac2-40be-83de-a3c3e171923c"
USER_ID4 = "4b85265f-d257-41a1-bed7-e0c34a5f030e"
USER_ID5 = "59e45134-772e-4b40-ab19-158f7d0bbb2e"


ROLE_ID1 = 'TEST1_NORMAL'
ROLE_ID2 = 'TEST1_SUPERROLE'
ROLE_ID3 = 'TEST2_PORTAL'
ROLE_ID4 = 'TEST2_NORMAL'


class GlobalRule(BaseRule):
    model = User
    actions = ALL_ACTIONS

    def scope_filter(self, request):
        return Q(first_name__isnull=False)


class EditCurrentUserRule(BaseRule):
    model = User
    actions = ['update']

    def scope_filter(self, request):
        return Q(pk=request.user.pk)


class AllActionFrenchPeopleRule(BaseRule):
    model = User
    actions = ALL_ACTIONS

    def scope_filter(self, request):
        return Q(language='fr')


class ReadOnlyDupon(BaseRule):
    model = User
    actions = ['list', 'retrieve']

    def scope_filter(self, request):
        return Q(username__icontains='dupon')


class TestAccessPolicy(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_1 = User.objects.create(
            pk=USER_ID1,
            first_name="Tintin",
            username="Tintin",
            password="MiL0u4ev3r",
            email="tintin@moulinsart.com",
            language='fr',
        )
        cls.user_2 = User.objects.create(
            pk=USER_ID2,
            first_name="Archibald",
            username="Haddock",
            password="MilleMilliardDeMillesabords",
            email="capitain@moulinsart.com",
            language='en-us',
        )
        cls.user_3 = User.objects.create(
            pk=USER_ID3,
            first_name="Tryphon",
            username="proftournesol",
            password="ObjectIfLuN3",
            email="Tryphon@moulinsart.com",
            language='fr',
        )
        cls.user_4 = User.objects.create(
            pk=USER_ID4,
            first_name="Unknown",
            username="dupont",
            password="avec_un_t",
            email="dupont@moulinsart.com",
            language='en-us',
        )
        cls.user_5 = User.objects.create(
            pk=USER_ID5,
            username="dupond",
            password="avec_un_d",
            email="dupond@moulinsart.com",
            language='fr',
        )

        cls.role_a, cls.role_b, cls.role_c, cls.role_d = UserRole.objects.bulk_create([
            UserRole(id=ROLE_ID1, name="Normal Role 1"),
            UserRole(id=ROLE_ID2, name="Super Role 1"),
            UserRole(id=ROLE_ID3, name="Portal Role 2"),
            UserRole(id=ROLE_ID4, name="Normal Role 2"),
        ])


    def setUp(self):
        super().setUp()
        self._old_rule_registry = access_policy._rule_registry
        access_policy._rule_registry = {}

        # register all test rules
        access_policy._register_rule(GlobalRule)
        access_policy._register_rule(EditCurrentUserRule, [ROLE_ID1])
        access_policy._register_rule(AllActionFrenchPeopleRule, [ROLE_ID2])
        access_policy._register_rule(ReadOnlyDupon, [ROLE_ID3])

        access_policy._register_rule(AllActionFrenchPeopleRule, [ROLE_ID4])
        access_policy._register_rule(ReadOnlyDupon, [ROLE_ID4])

    def tearDown(self):
        super().tearDown()
        access_policy._rule_registry = self._old_rule_registry

    @parameterized.expand(
        [
            (USER_ID1, 'list', [ROLE_ID1], [USER_ID1, USER_ID2, USER_ID3, USER_ID4]), # only global rule
            (USER_ID1, 'update', [ROLE_ID1], [USER_ID1]), # global + edit me
            (USER_ID3, 'update', [ROLE_ID1], [USER_ID3]), # global + edit me
            (USER_ID1, 'list', [ROLE_ID2], [USER_ID1, USER_ID3]),  # global + fr rule
            (USER_ID1, 'update', [ROLE_ID2], [USER_ID1, USER_ID3]),  # global + (fr rule | edit me)
            (USER_ID1, 'specific_action', [ROLE_ID2], [USER_ID1, USER_ID3]),  # global + fr rule
            (USER_ID1, 'list', [ROLE_ID3], [USER_ID4]),  # global + (dupon only)
            (USER_ID1, 'update', [ROLE_ID3], [USER_ID1, USER_ID2, USER_ID3, USER_ID4]),  # global
            (USER_ID1, 'list', [ROLE_ID4], [USER_ID1, USER_ID3, USER_ID4]),  # global + (dupon only | fr)
            (USER_ID1, 'update', [ROLE_ID4], [USER_ID1, USER_ID3]),  # global + fr
            (USER_ID1, 'specific_action', [ROLE_ID4], [USER_ID1, USER_ID3]),  # global + fr
        ]
    )
    def test_access_rules_through_roles(self, current_user_id, action, role_ids, expected_pks):
        user = User.objects.get(pk=current_user_id)
        roles = UserRole.objects.filter(pk__in=role_ids)

        user.roles.set(roles)

        queryset = User.objects.all()
        qs = apply_access_rules_sync(queryset, action, user=user)

        self.assertEqual({str(pk) for pk in qs.values_list('pk', flat=True)}, set(expected_pks))
