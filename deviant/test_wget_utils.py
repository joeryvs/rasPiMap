import unittest
from datetime import datetime, timezone

from wget_utils import parse_last_modified_header


class TestWget(unittest.TestCase):
    def test_parse_last_modified_header_01(self):

        a = "Sun, 12 Oct 2025 01:19:25 UTC"

        result = parse_last_modified_header(a)

        self.assertEqual(result, datetime(2025, 10, 12, 1, 19, 25, tzinfo=timezone.utc))

    def test_parse_last_modified_header_02(self):

        a = "Mon, 31 Jan 2000 23:41:59 GMT"

        result = parse_last_modified_header(a)

        self.assertEqual(result, datetime(2000, 1, 31, 23, 41, 59, tzinfo=timezone.utc))

    def test_parse_last_modified_header_invalid(self):
        invalid = ["", "12 Oct 2025 ", "01022000T010101"]

        for invalid_item in invalid:
            with self.subTest(invalid_item=repr(invalid_item)):
                result = parse_last_modified_header(invalid_item)
                self.assertIsNone(result)
