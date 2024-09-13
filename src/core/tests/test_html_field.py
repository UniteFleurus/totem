from django.test import TestCase
from parameterized import parameterized

from core import fields


class TestHTMLField(TestCase):
    def test_famoco_id_field(self):
        f = fields.HtmlField()

        msg = "Enter a valid Famoco ID, no parenthesis notation."
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean("ABCDEF", None)

        msg = "Enter a valid Famoco ID, no parenthesis notation."
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean("(01)03770004396238(21)236", None)

        msg = "Enter a valid Famoco ID, no parenthesis notation."
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean("ABCDEFZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ", None)

        msg = 'Ensure this value has at most 50 characters (it has 56).'
        with self.assertRaisesMessage(ValidationError, msg):
            f.clean("ABCDEFZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ", None)

        self.assertEqual(
            f.clean("010377000439623821236", None), "010377000439623821236"
        )

    def test_famoco_id_field_max_length(self):
        f1 = fields.FamocoIDField()
        f2 = fields.FamocoIDField(max_length=42)  # max_length is customisable
        self.assertIsNotNone(f1.formfield().max_length)
        self.assertEqual(f1.formfield().max_length, FAMOCO_ID_MAX_LENGTH)

        self.assertIsNotNone(f2.formfield().max_length)
        self.assertEqual(f2.formfield().max_length, 42)

    @parameterized.expand(
        [
            ('(01)03770004396245', False),
            ('(01)03770004396245(21)', False),
            ('(01)03770004396245(21)', False),
            ('(01)03770004396245(21)0', False),  # no zero after '21''
            ('(01)03760291064444(21)0', False),  # no zero after '21''
            ('(01)03760397554444(21)0', False),  # no zero after '21''
            ('(01)03770004396245(21)ZZZZZZ', True),
            # test 3 company prefixes
            ('(01)03770004396999(21)1', True),
            # must have 3 numbers after prefix
            ('(01)0377000439699(21)1', False),
            ('(01)03760291069999(21)1', True),
            # must have 4 numbers after prefix
            ('(01)0376029106999(21)1', False),
            ('(01)03760397559999(21)1', True),
            # must have 4 numbers after prefix
            ('(01)0376039755999(21)1', False),
        ]
    )
    def test_is_valid(self, famoco_id, is_valid):
        self.assertEqual(
            fields.FamocoIDField.is_valid_famoco_id(famoco_id), is_valid)

    @parameterized.expand(
        [
            # invalid famoco id
            ('(01)03770004396245', '(01)03770004396245()'),
            ('ABCDEFGHIJ', '(AB)CDEFGHIJ()'),
            # valid famoco id
            ('010377000439623821236', '(01)03770004396238(21)236'),
            ('0103770004396320211JMC', '(01)03770004396320(21)1JMC'),
            (
                '(01)03770004396320(21)1JMC',
                '(01)03770004396320(21)1JMC',
            ),  # already formatted
        ]
    )
    def test_format_famoco_id(self, famoco_id, formatted_famoco_id):
        self.assertEqual(
            fields.FamocoIDField.format_famoco_id(
                famoco_id), formatted_famoco_id
        )

    @parameterized.expand(
        [
            # invalid famoco id
            ('(01)03770004396245', '0103770004396245'),
            ('(AB)CDEFGHIJ()', 'ABCDEFGHIJ'),
            # valid famoco id
            ('(01)03770004396238(21)236', '010377000439623821236'),
            # already unformatted
            ('0103770004396320211JMC', '0103770004396320211JMC'),
        ]
    )
    def test_unformat_famoco_id(self, famoco_id, unformatted_famoco_id):
        self.assertEqual(
            fields.FamocoIDField.unformat_famoco_id(
                famoco_id), unformatted_famoco_id
        )
