from asgiref.sync import async_to_sync
from collections import namedtuple
from django.db.models import Q
from django.test import TestCase
from parameterized import parameterized

from user.models import User, UserRole
from user.access_policy import apply_access_rules, access_policy, BaseRule, Context

MockRequest = namedtuple('MockRequest', 'user')


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
    identifier = "user_global"
    model = User
    name = "Global Rule"

    def scope_filter(self, action, context):
        return Q(first_name__isnull=False)


class EditCurrentUserRule(BaseRule):
    identifier = "user_edit_own_profile"
    model = User
    name = "Edit only himself"

    def scope_filter(self, action, context):
        if action == 'update':
            return Q(pk=context.user.pk)
        return Q()


class AllActionFrenchPeopleRule(BaseRule):
    identifier = "user_crud_fr"
    model = User
    name = "Can CRUD French users"

    def scope_filter(self, action, context):
        return Q(language='fr')


class ReadOnlyDupon(BaseRule):
    identifier = "user_readonly_dupon"
    model = User
    name = "Can Read Dupon users"

    def scope_filter(self, action, context):
        if action in ['list', 'retrieve']:
            return Q(username__icontains='dupon')
        return Q()


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
            UserRole(id=ROLE_ID1, name="Normal Role 1", rules=[GlobalRule.identifier, EditCurrentUserRule.identifier]),
            UserRole(id=ROLE_ID2, name="Super Role 1", rules=[GlobalRule.identifier, AllActionFrenchPeopleRule.identifier]),
            UserRole(id=ROLE_ID3, name="Portal Role 2", rules=[GlobalRule.identifier, ReadOnlyDupon.identifier]),
            UserRole(id=ROLE_ID4, name="Normal Role 2", rules=[GlobalRule.identifier, AllActionFrenchPeopleRule.identifier, ReadOnlyDupon.identifier]),
        ])


    def setUp(self):
        super().setUp()
        self._old_rule_registry = access_policy._rule_registry
        self._old_rule_model_registry = access_policy._rule_model_registry
        access_policy._rule_registry = {}
        access_policy._rule_model_registry = {}

        # register all test rules
        access_policy._register_rule(GlobalRule)
        access_policy._register_rule(EditCurrentUserRule)
        access_policy._register_rule(AllActionFrenchPeopleRule)
        access_policy._register_rule(ReadOnlyDupon)

    def tearDown(self):
        super().tearDown()
        access_policy._rule_registry = self._old_rule_registry
        access_policy._rule_model_registry = self._old_rule_model_registry

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
            (USER_ID1, 'list', [ROLE_ID4], []),  # global + dupon only + fr
            (USER_ID1, 'update', [ROLE_ID4], [USER_ID1, USER_ID3]),  # global + fr
            (USER_ID1, 'specific_action', [ROLE_ID4], [USER_ID1, USER_ID3]),  # global + fr
            (USER_ID1, 'list', [ROLE_ID1, ROLE_ID4], [USER_ID1, USER_ID2, USER_ID3, USER_ID4]),  # global + dupon only
            (USER_ID1, 'update', [ROLE_ID1, ROLE_ID4], [USER_ID1, USER_ID3]),  # global + dupon only + edit me
        ]
    )
    def test_access_rules_through_roles(self, current_user_id, action, role_ids, expected_pks):
        user = User.objects.get(pk=current_user_id)
        roles = UserRole.objects.filter(pk__in=role_ids)

        user.roles.set(roles)
        context = Context(user=user)

        queryset = User.objects.all()
        qs = async_to_sync(apply_access_rules)(queryset, action, context)

        self.assertEqual({str(pk) for pk in qs.values_list('pk', flat=True)}, set(expected_pks))
