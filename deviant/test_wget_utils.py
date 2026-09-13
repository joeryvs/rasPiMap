# import unittest
from datetime import datetime, timezone
from unittest import TestCase, mock

from wget_utils import _detect_filename, _filename_fix_existing, _filename_from_url, parse_last_modified_header


class TestWget(TestCase):
    def test_filename_from_url_1(self):

        url1 = "https://www.example.com/test.png?hello=world#container"
        result1 = _filename_from_url(url1)

        self.assertEqual(result1, "test.png")

    def test_filename_from_url_2(self):

        url1 = "http://www.example.com/?hello=world#container"
        result1 = _filename_from_url(url1)

        self.assertIsNone(result1)

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

    def test_filename_fix_existing_no_others(self):

        with mock.patch("os.listdir") as mock_list_dir:
            mock_list_dir.return_value = ["example.png"]
            result = _filename_fix_existing("example.png")

            self.assertEqual(result, "example (1).png")

            mock_list_dir.return_value = ["hello"]
            result = _filename_fix_existing("hello")
            self.assertEqual(result, "hello (1)")

    def test_filename_fix_existing_no_others_in_directory(self):

        with mock.patch("os.listdir") as mock_list_dir:
            mock_list_dir.return_value = ["example.png"]
            result = _filename_fix_existing("foo/example.png")

            self.assertEqual(result, "foo/example (1).png")

            mock_list_dir.return_value = ["hello"]
            result = _filename_fix_existing("foo/hello")
            self.assertEqual(result, "foo/hello (1)")

    def test_filename_fix_existing_multiple(self):

        with mock.patch("os.listdir") as mock_list_dir:
            mock_list_dir.return_value = ["example.jpg", "example (1).jpg", "example (2).png", "example (3).webp"]
            result = _filename_fix_existing("example.jpg")

            self.assertEqual(result, "example (4).jpg")

            mock_list_dir.return_value = ["hello", "hello (1)", "hello (3)"]
            result = _filename_fix_existing("hello")
            self.assertEqual(result, "hello (4)")

    def test_filename_fix_existing_multiple_non_int(self):

        with mock.patch("os.listdir") as mock_list_dir:
            mock_list_dir.return_value = ["example.jpg", "example (a).jpg", "example (   ).png", "example (bar).webp"]
            result = _filename_fix_existing("example.jpg")

            self.assertEqual(result, "example (1).jpg")

            mock_list_dir.return_value = ["hello", "hello (1)", "hello (+)", "hello (!)"]
            result = _filename_fix_existing("hello")
            self.assertEqual(result, "hello (2)")
