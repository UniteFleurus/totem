from django.test import SimpleTestCase
from parameterized import parameterized
from pydantic import TypeAdapter, ValidationError, UUID4

from core.schemas.fields import ListOfString, ListOfSlug, ListOfInt, ListOfUUID


class SchemaCustomFieldTest(SimpleTestCase):

    @parameterized.expand(
        [
           ("my-String", ["my-String"], False),
           ("stringA,stringB", ["stringA", "stringB"], False),
           ("12,45", ["12", "45"], False)
        ]
    )
    def test_list_of_string(self, input_value, expected_result, raise_exc):
        if raise_exc:
            with self.assertRaises(ValidationError):
                TypeAdapter(ListOfString).validate_python(input_value)
        else:
            output = TypeAdapter(ListOfString).validate_python(input_value)
            self.assertEqual(output, expected_result)


    @parameterized.expand(
        [
           ("42", [42], False),
           ("12,45", [12, 45], False),
           ("stringA,stringB", None, True),
           ("stringA,c4ff7ff0-db84-4d23-a941-7646f597196d", None, True),
        ]
    )
    def test_list_of_int(self, input_value, expected_result, raise_exc):
        if raise_exc:
            with self.assertRaises(ValidationError):
                TypeAdapter(ListOfInt).validate_python(input_value)
        else:
            output = TypeAdapter(ListOfInt).validate_python(input_value)
            self.assertEqual(output, expected_result)


    @parameterized.expand(
        [
           ("c4ff7ff0-db84-4d23-a941-7646f597196d", [UUID4("c4ff7ff0-db84-4d23-a941-7646f597196d")], False),
           ("c4ff7ff0-db84-4d23-a941-7646f597196d,53318bcf-dba3-4a24-ac6d-f7e433919e21", [UUID4("c4ff7ff0-db84-4d23-a941-7646f597196d"), UUID4("53318bcf-dba3-4a24-ac6d-f7e433919e21")], False),
           ("42", None, True),
           ("12,45", None, True),
           ("stringA,stringB", None, True),
        ]
    )
    def test_list_of_uuid4(self, input_value, expected_result, raise_exc):
        if raise_exc:
            with self.assertRaises(ValidationError):
                TypeAdapter(ListOfUUID).validate_python(input_value)
        else:
            output = TypeAdapter(ListOfUUID).validate_python(input_value)
            self.assertEqual(output, expected_result)


    @parameterized.expand(
        [
           ("my-first-slug-1", ["my-first-slug-1"], False),
           ("my-first-slug-1,my-2nd-slug", ["my-first-slug-1","my-2nd-slug"], False),
           ("42", ["42"], False),
           ("42,45", ["42", "45"], False),
           ("s}tri*ngA,abcd.ef;ij", None, True),
        ]
    )
    def test_list_of_slug(self, input_value, expected_result, raise_exc):
        if raise_exc:
            with self.assertRaises(ValidationError):
                TypeAdapter(ListOfSlug).validate_python(input_value)
        else:
            output = TypeAdapter(ListOfSlug).validate_python(input_value)
            self.assertEqual(output, expected_result)
