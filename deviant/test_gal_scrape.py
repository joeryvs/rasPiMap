import unittest

from gal_scrape import _validate_user_name


class TestGalScrape(unittest.TestCase):
    def test_validate_user_name(self):
        valid_names = ["user", "2", "h5", "hello-world", "foo-8-bar3728baz"]
        for valid_name in valid_names:
            with self.subTest("%(valid_name)s is a valid user name", valid_name=valid_name):
                result = _validate_user_name(valid_name)
                self.assertEqual(valid_name, result)
        invalid_names = ["", " ", "\n", "\t", "hello world", "user#", "FOO"]
        for invalid_name in invalid_names:
            with self.subTest("%(invalid_name)% is not a valid user name", invalid_name=invalid_name):
                with self.assertRaises(ValueError):
                    result = _validate_user_name(user_name=invalid_name)
