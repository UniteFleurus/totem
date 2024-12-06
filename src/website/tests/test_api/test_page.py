from django.utils import timezone
from django.test import TestCase
from freezegun import freeze_time
from parameterized import parameterized

from core.testing import APITestCaseMixin
from website.models import Page
from .common import CommonTestMixin, USER_ID1, USER_ID2
from unittest.mock import MagicMock, patch

SLUG_1 = 'page-1'
SLUG_2 = 'page-two'
SLUG_3 = 'the-page-3'
SLUG_4 = 'page-4'
SLUG_5 = 'new-page'


@freeze_time("2024-11-18 11:12:13")
class PageTest(CommonTestMixin, APITestCaseMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.page1 = Page.objects.create(
            slug=SLUG_1,
            user=cls.user_frodon,
            is_published=True,
            date_published=timezone.now(),
            title="My Page One",
            content="<p>This is the content</p>",
        )
        cls.page2 = Page.objects.create(
            slug=SLUG_2,
            user=cls.user_frodon,
            is_published=False,
            date_published=None,
            title="My Page 2",
            content="<p>This is the content</p>",
        )
        cls.page3 = Page.objects.create(
            slug=SLUG_3,
            user=None,
            is_published=True,
            date_published=timezone.now(),
            title="The Page Three",
            content="<p>This is the content</p>",
        )
        cls.page4 = Page.objects.create(
            slug=SLUG_4,
            user=cls.user_gollum,
            is_published=False,
            date_published=None,
            title="Title of p4",
            content="<p>This is the content</p>",
        )

        cls.url = "/api/v1/website/pages/"
        cls.url_detail = f"/api/v1/website/pages/{SLUG_1}/"
        cls.payload_create = {
            "user": str(cls.user_frodon.pk),
            "slug": SLUG_5,
            "is_published": False,
            "date_published": "2024-09-04T13:21:13Z",
            "title": "Le Camp2",
            "content": "<p>This a <b>test</b></p>"
        }
        cls.payload_update = {
            "is_published": True,
            "title": "Le Nouveau titre",
            "content": "<p>This a <b>A NEW CONTENT</b></p>"
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
        self.assertEqual(len(data["results"]), 4)
        self.assertEqual(data["count"], 4)

        for item in data["results"]:
            obj = Page.objects.get(slug=item["slug"])
            self._assert_api_format(item, obj, [
                "slug",
                "title",
                "user",
                "url",
                "is_published",
                "date_published",
                "update_date",
            ])

    @parameterized.expand(
        [
            ({'title': 'Title'}, [SLUG_4]),
            ({'title': 'Page'}, [SLUG_1, SLUG_2, SLUG_3]),
            ({'is_published': True}, [SLUG_1, SLUG_3]),
            ({'is_published': False}, [SLUG_2, SLUG_4]),
            ({'is_published': False}, [SLUG_2, SLUG_4]),
            ({'user': f"{USER_ID1}"}, [SLUG_1, SLUG_2]),
            ({'user': f"{USER_ID1},{USER_ID2}"}, [SLUG_1, SLUG_2, SLUG_4]),
        ]
    )
    def test_list_filters(self, filters, slugs):
        qs = Page.objects.filter(slug__in=slugs)

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
            obj = qs.get(slug=item["slug"])
            self._assert_api_format(item, obj, [
                "slug",
                "title",
                "user",
                "url",
                "is_published",
                "date_published",
                "update_date",
            ])

    @parameterized.expand(
        [
            ({'user': "invalid uuid"},),
        ]
    )
    def test_list_invalid_filters(self, filters):
        response = self.do_api_request(self.url, "GET", self.user_access_token_frodon.token, params=filters)
        self.assertEqual(response.status_code, 422)

    @parameterized.expand(
        [
            ([], ['date_published', 'id']), # default
            (['slug'], ['slug']),
            (['-slug'], ['-slug']),
            (['title'], ['title']),
            (['-title'], ['-title']),
            (['date_published'], ['date_published']),
            (['-date_published'], ['-date_published']),
        ]
    )
    def test_list_ordering(self, ordering_fields, order_by):
        ordering = ','.join(ordering_fields)
        params = {}
        if ordering:
            params = {'ordering': ordering}
        response = self.do_api_request(self.url, "GET", self.user_access_token_frodon.token, params=params)
        data = response.json()

        queryset = Page.objects.all().order_by(*order_by)

        for instance, item in zip(queryset, data["results"]):
            self.assertEqual(str(instance.slug), item["slug"])

    @parameterized.expand(
        [
            ('Title', [SLUG_4]),
            ('Page', [SLUG_1, SLUG_2, SLUG_3]),
            ('no-match', []),
        ]
    )
    def test_list_searching(self, search_term, slugs):
        qs = Page.objects.filter(slug__in=slugs)

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
            obj = qs.get(slug=item["slug"])
            self._assert_api_format(item, obj, [
                "slug",
                "title",
                "user",
                "url",
                "is_published",
                "date_published",
                "update_date",
            ])

    @parameterized.expand(
        [
            ("totem.websitepage.create", 403),
            ("totem.websitepage.read", 200),
            ("totem.websitepage.update", 403),
            ("totem.websitepage.delete", 403),
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
    # Detail Operation
    #------------------------------------------

    def test_detail_response(self):
        response = self.do_api_request(self.url_detail, 'GET', self.user_access_token_frodon.token)
        data = response.json()

        self.assertEqual(response.status_code, 200)

        obj = Page.objects.get(slug=SLUG_1)
        self._assert_api_format(data, obj, [
            "slug",
            "title",
            "user",
            "url",
            "is_published",
            "date_published",
            "update_date",
            "content",
        ])

    @parameterized.expand(
        [
            ("totem.websitepage.create", 403),
            ("totem.websitepage.read", 200),
            ("totem.websitepage.update", 403),
            ("totem.websitepage.delete", 403),
        ]
    )
    def test_detail_access_rights(self, scope, status_code):
        self.user_access_token_frodon.scope = scope
        self.user_access_token_frodon.save(update_fields=["scope"])

        response = self.do_api_request(self.url_detail, 'GET', self.user_access_token_frodon.token)
        data = response.json()

        self.assertEqual(response.status_code, status_code)
        if status_code != 200:
            self.assertEqual(data, {'detail': 'You do not have permission to perform this action.'})

    #------------------------------------------
    # Create Operation
    #------------------------------------------

    @parameterized.expand(
        [
            ({"user": None}, 201),
            ({"user": "945fdf86-879c-45c4-bd23-e5818a16c253"}, 422), # non existing user
            ({"slug": SLUG_1}, 400), # already existing slug (unique constraint)
            ({"slug": "not a slug"}, 422), # wrong slug
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

        obj = Page.objects.get(slug=SLUG_5)
        self._assert_api_format(data, obj, [
            "slug",
            "title",
            "user",
            "url",
            "is_published",
            "date_published",
            "update_date",
            "content",
        ], expand=True)

    @parameterized.expand(
        [
            ("totem.websitepage.create", 201),
            ("totem.websitepage.read", 403),
            ("totem.websitepage.update", 403),
            ("totem.websitepage.delete", 403),
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
            ({"title": None}, 422),
            ({"user": None}, 200),
            ({"user": "945fdf86-879c-45c4-bd23-e5818a16c253"}, 422), # non existing user
            ({"slug": SLUG_5}, 200), # non existing new slug
            ({"slug": "not a slug"}, 422), # wrong slug
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

        obj = Page.objects.get(slug=SLUG_1)
        self._assert_api_format(data, obj, [
            "slug",
            "title",
            "user",
            "url",
            "is_published",
            "date_published",
            "update_date",
            "content",
        ], expand=True)

    @parameterized.expand(
        [
            ("totem.websitepage.create", 403),
            ("totem.websitepage.read", 403),
            ("totem.websitepage.update", 200),
            ("totem.websitepage.delete", 403),
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
            ("totem.websitepage.create", 403),
            ("totem.websitepage.read", 403),
            ("totem.websitepage.update", 403),
            ("totem.websitepage.delete", 204),
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
                "slug",
                "title",
                "user",
                "url",
                "is_published",
                "date_published",
                "update_date",
            ]
        if "slug" in fields:
            self.assertEqual(api_data["slug"], obj.slug)
        if "title" in fields:
            self.assertEqual(api_data["title"], obj.title)
        if "user" in fields:
            data = str(obj.user_id) if obj.user_id else None
            if expand:
                if data:
                    data = {"id": str(obj.user.id), "username": obj.user.username}
            self.assertEqual(
                api_data["user"],
                data,
            )
        if "url" in fields:
            self.assertEqual(api_data["url"], obj.url)
        if "is_published" in fields:
            self.assertEqual(api_data["is_published"], obj.is_published)
        if "date_published" in fields:
            self.assertEqual(api_data["date_published"], obj.date_published.strftime("%Y-%m-%dT%H:%M:%SZ") if obj.date_published else None)
        if "update_date" in fields:
            self.assertEqual(api_data["update_date"], obj.update_date.strftime("%Y-%m-%dT%H:%M:%SZ") if obj.update_date else None)

        self.assertEqual(
            set(fields),
            set(api_data.keys()),
        )
