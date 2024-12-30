from django.utils import timezone
from django.test import TestCase
from freezegun import freeze_time
from parameterized import parameterized

from core.testing import APITestCaseMixin
from website.models import Menu, Page
from .common import CommonTestMixin

ROOT_ID = '2a9c3e12-c072-4bf7-9d18-e66d72599f7b'
MENU_1 = '09c7b4f5-b436-4c47-bea1-d3e60b9ab492'
MENU_2 = 'cf612f7c-b35f-4416-8e5f-6c36e7e32e99'
MENU_3 = '8632bc93-e692-43de-b873-34610551afcd'
MENU_4 = '47c95f9e-19fb-43d0-b9e2-295f7b134615'
MENU_5 = 'ad71730c-1967-439b-958b-f0c01167a97e' # not existing

SLUG_1 = 'page-1'
SLUG_2 = 'page-non-existing'


@freeze_time("2024-11-18 11:12:13")
class MenuTest(CommonTestMixin, APITestCaseMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.page1 = Page.objects.create(
            slug=SLUG_1,
            is_published=True,
            date_published=timezone.now(),
            title="My Page One",
            content="<p>This is the content</p>",
        )

        cls.root_menu = Menu.objects.create(
            id=ROOT_ID,
            parent=None,
            new_window=False,
            page=None,
            link=None,
        )

        cls.menu1 = Menu.objects.create(
            id=MENU_1,
            parent=cls.root_menu,
            new_window=True,
            page=cls.page1,
            name="My Menu One",
        )
        cls.menu2 = Menu.objects.create(
            id=MENU_2,
            parent=cls.root_menu,
            new_window=False,
            create_date=None,
            name="My Menu 2",
            link="/events",
        )
        cls.menu3 = Menu.objects.create(
            id=MENU_3,
            new_window=True,
            page=cls.page1,
            name="The Menu Three",
        )
        cls.menu4 = Menu.objects.create(
            id=MENU_4,
            new_window=False,
            create_date=None,
            name="Title of m4",
            link="http://www.anotherwebsite.com",
        )

        cls.url = "/api/v1/website/menus/"
        cls.url_detail = f"/api/v1/website/menus/{MENU_1}/"
        cls.payload_create = {
            "parent": str(cls.root_menu.pk),
            "page": str(cls.page1.slug),
            "new_window": False,
            "name": "My Menu Name",
        }
        cls.payload_update = {
            "name": "My New Name",
            "new_window": True,
            "page": None,
            "link": "https://www.otherwebsite.com",
            "parent": str(cls.menu4.pk),
        }

    #------------------------------------------
    # List Operation
    #------------------------------------------

    def test_list_response(self):
        response = self.do_api_request(self.url, 'GET', self.user_access_token_frodon.token)
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("count", data)
        self.assertIn("results", data)
        self.assertIn("next", data)
        self.assertIn("previous", data)
        self.assertEqual(len(data["results"]), 5)
        self.assertEqual(data["count"], 5)

        for item in data["results"]:
            obj = Menu.objects.get(id=item["id"])
            self._assert_api_format(item, obj, [
                "id",
                "name",
                "page",
                "parent",
                "link",
                "new_window",
                "create_date",
                "sequence",
            ])

    @parameterized.expand(
        [
            ({'name': 'Title'}, [MENU_4]),
            ({'name': 'Menu'}, [MENU_1, MENU_2, MENU_3]),
            ({'new_window': True}, [MENU_1, MENU_3]),
            ({'new_window': False}, [ROOT_ID, MENU_2, MENU_4]),
            ({'page_slug': SLUG_1}, [MENU_1, MENU_3]),
            ({'parent': ROOT_ID}, [MENU_1, MENU_2]),
        ]
    )
    def test_list_filters(self, filters, ids):
        qs = Menu.objects.filter(pk__in=ids)

        response = self.do_api_request(self.url, "GET", self.user_access_token_frodon.token, params=filters)
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("count", data)
        self.assertIn("results", data)
        self.assertIn("next", data)
        self.assertIn("previous", data)
        self.assertEqual(len(data["results"]), len(qs))
        self.assertEqual(data["count"], len(qs))

        for item in data["results"]:
            obj = qs.get(id=item["id"])
            self._assert_api_format(item, obj, [
                "id",
                "name",
                "page",
                "parent",
                "link",
                "new_window",
                "create_date",
                "sequence",
            ])

    @parameterized.expand(
        [
            ({'parent': "invalid uuid"},),
            ({'page_slug': "invalid.slug!"},),
        ]
    )
    def test_list_invalid_filters(self, filters):
        response = self.do_api_request(self.url, "GET", self.user_access_token_frodon.token, params=filters)
        self.assertEqual(response.status_code, 422)

    @parameterized.expand(
        [
            ([], ['sequence', 'name']), # default
            (['id'], ['id']),
            (['-id'], ['-id']),
            (['name'], ['name']),
            (['-name'], ['-name']),
            (['sequence'], ['sequence']),
            (['-sequence'], ['-sequence']),
            (['create_date'], ['create_date']),
            (['-create_date'], ['-create_date']),
        ]
    )
    def test_list_ordering(self, ordering_fields, order_by):
        ordering = ','.join(ordering_fields)
        params = {}
        if ordering:
            params = {'ordering': ordering}
        response = self.do_api_request(self.url, "GET", self.user_access_token_frodon.token, params=params)
        data = response.json()

        queryset = Menu.objects.all().order_by(*order_by)

        for instance, item in zip(queryset, data["results"]):
            self.assertEqual(str(instance.pk), item["id"])

    @parameterized.expand(
        [
            ('Title', [MENU_4]),
            ('Menu', [MENU_1, MENU_2, MENU_3]),
            ('no-match', []),
        ]
    )
    def test_list_searching(self, search_term, ids):
        qs = Menu.objects.filter(pk__in=ids)

        response = self.do_api_request(self.url, "GET", self.user_access_token_frodon.token, params={'search': search_term})
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("count", data)
        self.assertIn("results", data)
        self.assertIn("next", data)
        self.assertIn("previous", data)
        self.assertEqual(len(data["results"]), len(qs))
        self.assertEqual(data["count"], len(qs))

        for item in data["results"]:
            obj = qs.get(pk=item["id"])
            self._assert_api_format(item, obj, [
                "id",
                "name",
                "page",
                "parent",
                "link",
                "new_window",
                "create_date",
                "sequence",
            ])

    @parameterized.expand(
        [
            ("totem.websitemenu.create", 403),
            ("totem.websitemenu.read", 200),
            ("totem.websitemenu.update", 403),
            ("totem.websitemenu.delete", 403),
        ]
    )
    def test_list_access_rights(self, scope, status_code):
        self.user_access_token_frodon.scope = scope
        self.user_access_token_frodon.save(update_fields=["scope"])

        response = self.do_api_request(self.url, 'GET', self.user_access_token_frodon.token)
        data = response.json()

        self.assertEqual(response.status_code, status_code)
        if status_code != 200:
            self.assertEqual(data, {'detail': 'You do not have permission to perform this action.'})

    #------------------------------------------
    # Create Operation
    #------------------------------------------

    @parameterized.expand(
        [
            ({"sequence": None}, 422),
            ({"parent": None}, 201),
            ({"parent": "945fdf86-879c-45c4-bd23-e5818a16c253"}, 422), # non existing parent menu
            ({"page": None, "link": "http://supersite.com"}, 201),
            ({"page": None, "link": None}, 400), # triggered by SQL integrity.
            ({"page": SLUG_1, "link": "http://supersite.com"}, 201), # TODO maybe we should prevent setting both
            ({"page": SLUG_2}, 422), # non existing page
        ]
    )
    def test_create_request_field_validation(self, extra_body, status_code):
        data = self.payload_create
        data.update(extra_body)

        response = self.do_api_request(self.url, 'POST', self.user_access_token_frodon.token, data=data)
        data = response.json()

        self.assertEqual(response.status_code, status_code)

    def test_create_response(self):
        response = self.do_api_request(self.url, 'POST', self.user_access_token_frodon.token, data=self.payload_create)
        data = response.json()

        self.assertEqual(response.status_code, 201)

        obj = Menu.objects.get(id=data['id'])
        self._assert_api_format(data, obj, [
            "id",
            "name",
            "page",
            "parent",
            "link",
            "new_window",
            "create_date",
            "sequence",
        ], expand=True)

    @parameterized.expand(
        [
            ("totem.websitemenu.create", 201),
            ("totem.websitemenu.read", 403),
            ("totem.websitemenu.update", 403),
            ("totem.websitemenu.delete", 403),
        ]
    )
    def test_create_access_rights(self, scope, status_code):
        self.user_access_token_frodon.scope = scope
        self.user_access_token_frodon.save(update_fields=["scope"])

        response = self.do_api_request(self.url, 'POST', self.user_access_token_frodon.token, data=self.payload_create)
        data = response.json()

        self.assertEqual(response.status_code, status_code)
        if status_code != 201:
            self.assertEqual(data, {'detail': 'You do not have permission to perform this action.'})

    #------------------------------------------
    # Update Operation
    #------------------------------------------

    @parameterized.expand(
        [
            ({"name": "new name"}, 200),
            ({"name": None}, 422),
            ({"sequence": 42}, 200),
            ({"page": None}, 200),
            ({"page": SLUG_2}, 422), # non existing page
            ({"page": "coucou.#ç"}, 422), # invalid slug
            ({"parent": None}, 200),
            ({"parent": MENU_5}, 422), # non existing parent
        ]
    )
    def test_update_request_field_validation(self, extra_body, status_code):
        data = self.payload_update
        data.update(extra_body)

        response = self.do_api_request(self.url_detail, 'PATCH', self.user_access_token_frodon.token, data=data)
        data = response.json()

        self.assertEqual(response.status_code, status_code)

    def test_update_response(self):
        response = self.do_api_request(self.url_detail, 'PATCH', self.user_access_token_frodon.token, data=self.payload_update)
        data = response.json()

        self.assertEqual(response.status_code, 200)

        obj = Menu.objects.get(id=MENU_1)
        self._assert_api_format(data, obj, [
            "id",
            "name",
            "page",
            "parent",
            "link",
            "new_window",
            "create_date",
            "sequence",
        ], expand=True)

    @parameterized.expand(
        [
            ("totem.websitemenu.create", 403),
            ("totem.websitemenu.read", 403),
            ("totem.websitemenu.update", 200),
            ("totem.websitemenu.delete", 403),
        ]
    )
    def test_update_access_rights(self, scope, status_code):
        self.user_access_token_frodon.scope = scope
        self.user_access_token_frodon.save(update_fields=["scope"])

        response = self.do_api_request(self.url_detail, 'PATCH', self.user_access_token_frodon.token, data=self.payload_update)
        data = response.json()

        self.assertEqual(response.status_code, status_code)
        if status_code != 200:
            self.assertEqual(data, {'detail': 'You do not have permission to perform this action.'})

    #------------------------------------------
    # Delete Operation
    #------------------------------------------

    def test_delete_response(self):
        response = self.do_api_request(self.url_detail, 'DELETE', self.user_access_token_frodon.token)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b'')

    @parameterized.expand(
        [
            ("totem.websitemenu.create", 403),
            ("totem.websitemenu.read", 403),
            ("totem.websitemenu.update", 403),
            ("totem.websitemenu.delete", 204),
        ]
    )
    def test_delete_access_rights(self, scope, status_code):
        self.user_access_token_frodon.scope = scope
        self.user_access_token_frodon.save(update_fields=["scope"])

        response = self.do_api_request(self.url_detail, 'DELETE', self.user_access_token_frodon.token)

        self.assertEqual(response.status_code, status_code)
        if status_code != 204:
            data = response.json()
            self.assertEqual(data, {'detail': 'You do not have permission to perform this action.'})

    #------------------------------------------
    # Utils
    #------------------------------------------

    def _assert_api_format(self, api_data, obj, fields, expand=True):
        if not fields:
            fields = [
                "id",
                "name",
                "parent",
                "page",
                "link",
                "sequence",
                "create_date",
                "new_window",
            ]
        if "id" in fields:
            self.assertEqual(api_data["id"], str(obj.id))
        if "name" in fields:
            self.assertEqual(api_data["name"], obj.name)
        if "parent" in fields:
            data = str(obj.parent_id) if obj.parent_id else None
            if expand:
                if data:
                    data = {"id": str(obj.parent.id), "name": obj.parent.name}
            self.assertEqual(
                api_data["parent"],
                data,
            )
        if "page" in fields:
            data = str(obj.page_id) if obj.page_id else None
            if expand:
                if data:
                    data = {"slug": str(obj.page.slug), "title": obj.page.title}
            self.assertEqual(
                api_data["page"],
                data,
            )
        if "sequence" in fields:
            self.assertEqual(api_data["sequence"], obj.sequence)
        if "link" in fields:
            self.assertEqual(api_data["link"], obj.link)
        if "new_window" in fields:
            self.assertEqual(api_data["new_window"], obj.new_window)
        if "create_date" in fields:
            self.assertEqual(api_data["create_date"], obj.create_date.strftime("%Y-%m-%dT%H:%M:%SZ") if obj.create_date else None)

        self.assertEqual(
            set(fields),
            set(api_data.keys()),
        )
