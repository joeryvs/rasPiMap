import unittest

import webscrape_extractors
from bs4 import BeautifulSoup


class TestBaseExtractor(unittest.TestCase):
    def test_error_when_constructing_raw_extractor(self):

        self.assertRaises(TypeError, webscrape_extractors.Extractor)


class TestImageExtractor(unittest.TestCase):
    def test_regex_matches(self):

        self.extractor = webscrape_extractors.ImageExtractor()
        regex = self.extractor._regex()
        match_urls = [
            "https://www.example.com",
            "https://www.example.com/test1/level2/more",
            "https://www.example.com?a=b&w=e&u=23#id",
            "https://",
            "https://x.com                spaties",
            "https://\x00null-character",
        ]

        for url in match_urls:
            with self.subTest(url=url, regex=regex):
                # self.assertTrue(regex.match(url))
                self.assertRegex(url, regex)

        no_match_urls = [
            "http://www.example.com",
            "udp://www.example.com",
            "file://www.example.com",
            "chrome://www.example.com",
            "ftp://www.example.com",
            "",
            "1",
        ]
        for url in no_match_urls:
            with self.subTest(url=url, regex=regex):
                self.assertNotRegex(url, regex)

    def test_retrieve_img_src(self):

        html = """<img alt='test' src='https://1.png' srcset='https://2.png 2x, https://3.png 4x'/>"""
        anchor = BeautifulSoup(html, "html.parser").find("img")
        self.extractor = webscrape_extractors.ImageExtractor()

        sources = list(self.extractor.retrieve_img_src(anchor))

        expected = [("https://1.png", "main"), ("https://2.png", "2x"), ("https://3.png", "4x")]
        self.assertListEqual(sources, expected)
        self.assertEqual(sources, expected)
        self.assertEqual(len(sources), 3)

    def test_retrieve_img_src_when_no_space_after_comma(self):
        html = """<img alt='test' src='https://1.png' srcset='https://2.png 2x,https://3.png 4x'/>"""
        anchor = BeautifulSoup(html, "html.parser").find("img")
        self.extractor = webscrape_extractors.ImageExtractor()

        sources = list(self.extractor.retrieve_img_src(anchor))

        expected = [("https://1.png", "main"), ("https://2.png", "2x"), ("https://3.png", "4x")]
        self.assertListEqual(sources, expected)
        self.assertEqual(sources, expected)
        self.assertEqual(len(sources), 3)

    def test_retrieve_img_src_when_url_contains_comma(self):
        html = """<img alt='test' src='https://1.png' srcset='https://2.png 2x, https://3,5.png 4x'/>"""
        anchor = BeautifulSoup(html, "html.parser").find("img")
        self.extractor = webscrape_extractors.ImageExtractor()

        sources = list(self.extractor.retrieve_img_src(anchor))

        expected = [("https://1.png", "main"), ("https://2.png", "2x"), ("https://3.png", "4x")]
        self.assertListEqual(sources, expected)
        self.assertEqual(sources, expected)
        self.assertEqual(len(sources), 3)


class TestAvatarExtractor(unittest.TestCase):
    def test_regex_matches(self):

        self.extractor = webscrape_extractors.AvatarExtractor()
        regex = self.extractor._regex()
        self.assertNotRegex("https://www.example.com/test1/level2/more", regex)
        self.assertRegex("https://a.deviantart.net/avatars-big/t/_/t-222.jpg?6", regex)
        self.assertRegex("https://a.deviantart.net/avatars-big/t/h/therealejoseph.jpg?9", regex)
        self.assertRegex("https://a.deviantart.net/avatars-big/t/i/tinomadethat.jpg", regex)
        self.assertRegex("https://a.deviantart.net/avatars-big/v/o/voidenbyte.jpg?2", regex)
        self.assertRegex("https://a.deviantart.net/avatars-big/y/o/youtheguilty.jpg?6", regex)
        self.assertNotRegex("http://a.deviantart.net/avatars-big/y/o/youtheguilty.jpg?6", regex)
        self.assertNotRegex("https://www.example.com", regex)


class TestMainImageExtractor(unittest.TestCase):
    def test_retrieve_img_src(self):

        html = """<img alt='test' src='https://1.png' srcset='https://2.png 2x, https://3.png 4x'/>"""
        anchor = BeautifulSoup(html, "html.parser").find("img")
        self.extractor = webscrape_extractors.MainImageExtractor()

        self.assertFalse(self.extractor._include_srcset)

        sources = list(self.extractor.retrieve_img_src(anchor))

        expected = [("https://1.png", "main")]
        self.assertListEqual(sources, expected)
        self.assertEqual(sources, expected)
        self.assertEqual(len(sources), 1)


class TestExtractorFactory(unittest.TestCase):
    def setUp(self) -> None:
        self.factory = webscrape_extractors.ExtractorFactory()
        return super().setUp()

    def test_contains_keys(self):

        self.assertIn("images", self.factory.choices)
        self.assertIn("images2x", self.factory.choices)
        self.assertIn("art", self.factory.choices)
        self.assertIn("users", self.factory.choices)
        self.assertIn("all_images", self.factory.choices)
        self.assertIn("large_images", self.factory.choices)
        self.assertIn("no_crop", self.factory.choices)
        self.assertIn("description", self.factory.choices)

    def test_extractor_is_build(self):

        imageExt = self.factory.extractor("images")
        self.assertIsInstance(imageExt, webscrape_extractors.Extractor)

    def test_invalid_key_gives_error(self):

        self.assertRaises(KeyError, lambda: self.factory.extractor("404"))


if __name__ == "__main__":
    unittest.main()
