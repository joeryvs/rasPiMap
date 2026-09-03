import unittest

from main import YtPostScraper, YtState


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
