
from parameterized import parameterized

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from core import fields


class TestHTMLField(SimpleTestCase):

    @parameterized.expand(
        [
            ("ABCDEF", False),
            ("<p>no ending tag", False),
            ("<p>A paragraph</p>", True),
            # ("<html>A paragraph</html>", True), will output <div><html>A paragraph</html></div>. no kill of html tag --> bug
            ("<p>A paragraph</p><p>A 2nd paragraph</p>", False),
        ]
    )
    def test_html_field_validator(self, input_html, is_valid):
        f = fields.HtmlField()

        if is_valid:
            self.assertEqual(
                f.clean(input_html, None), input_html
            )
        else:
            msg = "Content is not a valid html."
            with self.assertRaisesMessage(ValidationError, msg):
                f.clean(input_html, None)
