import unittest

from youtube import YtFactory, YtPostScraper, YtState


class TestYTSTate(unittest.TestCase):
    def test_ytstate(self):
        c = "abc"
        t = "token"
        graft_url = "https://example.com/test"

        state = YtState(c, t, graft_url)

        DATARAW = state.get_data_raw()

        self.assertIsInstance(DATARAW, dict)

        self.assertEqual(graft_url, DATARAW["context"]["client"]["mainAppWebInfo"]["graftUrl"])

        self.assertEqual(t, DATARAW["context"]["clickTracking"]["clickTrackingParams"])
        self.assertEqual(c, DATARAW["continuation"])


class TestYTScraper(unittest.TestCase):
    def test_scraper_url_from_initial(self):
        scraper = YtPostScraper(base_dir=None, graft_url="https://example.com", wait_time=0.0)

        result = scraper.urls_from_initial(None)
        self.assertEqual(result, [])

    def test_scraper_url_from_json_1(self):
        scraper = YtPostScraper(base_dir=None, graft_url="https://example.com", wait_time=0.0)

        result = scraper.urls_from_json({})
        self.assertEqual(result, [])

    def test_scraper_url_from_json_2(self):
        scraper = YtPostScraper(base_dir=None, graft_url="https://example.com", wait_time=0.0)

        result = scraper.urls_from_json({"url": "a", "test": "b", "nodes": [{"url": "c"}]})
        self.assertEqual(result, ["a", "c"])


class TestFactory(unittest.TestCase):
    def test_construction(self):
        factory = YtFactory("example")

        self.assertIsNotNone(factory)

    def test_invalid_construction(self):
        user = ""
        self.assertRaises(AssertionError, lambda: YtFactory(user=user))

        user = "\x01hello-world"
        self.assertRaises(AssertionError, lambda: YtFactory(user=user))

    def test_keep_url(self):

        factory = YtFactory("example")

        urls = [
            "https://yt3.ggpht.com/I",
        ]
        for url in urls:
            with self.subTest(url=url):
                result = factory.keep_url(url=url)
                self.assertTrue(result)
        invalid_urls = [
            "https://yt3.googleusercontent.com/2gEQWk9ws0NNWIOva0M7NwU9LtIDHfNvY0nLGdhqNvDUn3Sk4kNsTZQZ_ILl70CQrjKSZjhqAP0=s200-c-k-c0x00ffffff-no-rj?days_since_epoch=20702",
            "https://www.youtube.com/channel/UC1sELGmy5jp5fQUugmuYlXQ",
            "https://accounts.google.com/ServiceLogin?service=youtube&uilel=3&passive=true&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Dnl%26next%3D%252F&hl=nl",
        ]
        for url in invalid_urls:
            with self.subTest(url=url):
                result = factory.keep_url(url=url)
                self.assertFalse(result)

    def test_post_proces_url(self):

        factory = YtFactory("example")

        initial = "https://yt3.ggpht.com/-atVNbAGjDuhZ3bD4PPqb16WtWbdZDOXVw81W76-e1lBnkBLRq8ItY3_iKaaqe4O4ffIyW5eb5x7=s640-c-fcrop64=1,00000000ffffffff-rw-nd-v1"
        expected = "https://yt3.ggpht.com/-atVNbAGjDuhZ3bD4PPqb16WtWbdZDOXVw81W76-e1lBnkBLRq8ItY3_iKaaqe4O4ffIyW5eb5x7=s4000-rw-nd-v1"

        result = factory.post_process_url(initial)
        self.assertEqual(expected, result)
