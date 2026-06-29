import unittest
from abc import ABC, abstractmethod

import webscrape_extractors


class TestBaseExtractor(unittest.TestCase):
    def test_error_when_constructing_raw(self):

        self.assertRaises(TypeError, webscrape_extractors.Extractor)


class TestImageExtractor(unittest.TestCase):
    def setUp(self) -> None:
        self.extractor = webscrape_extractors.ImageExtractor()
        return super().setUp()

    def test_regex_matches(self):

        regex = self.extractor._regex()
        self.assertTrue(regex.match("https://www.example.com"))
        self.assertTrue(regex.match("https://www.example.com/test1/level2/more"))
        self.assertTrue(regex.match("https://www.example.com?a=b&w=e&u=23#id"))
        self.assertTrue(regex.match("https://"))
        self.assertTrue(regex.match("https://x.com                spaties"))
        self.assertTrue(regex.match("https://\x00null-character"))

        self.assertFalse(regex.match("http://www.example.com"))
        self.assertFalse(regex.match("udp://www.example.com"))
        self.assertFalse(regex.match("file://www.example.com"))
        self.assertFalse(regex.match("chrome://www.example.com"))
        self.assertFalse(regex.match("ftp://www.example.com"))


class TestAvatarExtractor(unittest.TestCase):
    def setUp(self) -> None:
        self.extractor = webscrape_extractors.AvatarExtractor()
        return super().setUp()

    def test_regex_matches(self):

        regex = self.extractor._regex()
        self.assertFalse(regex.match("https://www.example.com/test1/level2/more"))
        self.assertTrue(regex.match("https://a.deviantart.net/avatars-big/t/_/t-222.jpg?6"))
        self.assertTrue(regex.match("https://a.deviantart.net/avatars-big/t/h/therealejoseph.jpg?9"))
        self.assertTrue(regex.match("https://a.deviantart.net/avatars-big/t/i/tinomadethat.jpg"))
        self.assertTrue(regex.match("https://a.deviantart.net/avatars-big/v/o/voidenbyte.jpg?2"))
        self.assertTrue(regex.match("https://a.deviantart.net/avatars-big/y/o/youtheguilty.jpg?6"))
        self.assertFalse(regex.match("http://a.deviantart.net/avatars-big/y/o/youtheguilty.jpg?6"))
        self.assertFalse(regex.match("https://www.example.com"))


class TestFactory(unittest.TestCase):
    def setUp(self) -> None:
        self.factory = webscrape_extractors.ExtractorFactory()
        return super().setUp()

    def test_contains_keys(self):

        self.assertIn("images", self.factory.choices)
        self.assertIn("art", self.factory.choices)
        self.assertIn("users", self.factory.choices)
        self.assertIn("all_images", self.factory.choices)
        self.assertIn("no_crop", self.factory.choices)

    def test_extractor_is_build(self):

        imageExt = self.factory.extractor("images")
        self.assertIsInstance(imageExt, webscrape_extractors.Extractor)

    def test_invalid_key_gives_error(self):

        self.assertRaises(KeyError, lambda: self.factory.extractor("404"))


if __name__ == "__main__":
    unittest.main()
