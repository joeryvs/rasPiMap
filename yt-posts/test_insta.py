import unittest

from insta import InstagramFactory, InstaScraper, InstaState


class TestInstaSTate(unittest.TestCase):
    def test_ytstate(self):
        end_cursor = "abc"
        graft_url = "https://example.com/test"
        id_ = "1234567890123"

        state = InstaState(end_cursor=end_cursor, has_next_page=True, id=id_)

        DATARAW = state.get_data_raw()

        self.assertIsInstance(DATARAW, str)


class TestInstaScraper(unittest.TestCase):
    def test_scraper_url_from_initial(self):
        # TODO
        pass

    def test_scraper_url_from_json_1(self):
        scraper = InstaScraper(base_dir=None, base_url="https://example.com", wait_time=0.0)

        result = scraper.urls_from_json({})
        self.assertEqual(result, [])

    def test_scraper_url_from_json_2(self):
        scraper = InstaScraper(base_dir=None, base_url="https://example.com", wait_time=0.0)

        result = scraper.urls_from_json({"display_uri": "a", "test": "b", "nodes": [{"display_uri": "c"}]})
        self.assertEqual(result, ["a", "c"])


class TestFactory(unittest.TestCase):
    def test_construction(self):
        factory = InstagramFactory("example")

        self.assertIsNotNone(factory)

    def test_invalid_construction(self):
        user = ""
        self.assertRaises(AssertionError, lambda: InstagramFactory(user=user))

        user = "\x01hello-world"
        self.assertRaises(AssertionError, lambda: InstagramFactory(user=user))

    def test_keep_url(self):

        factory = InstagramFactory("example")

        urls = [
            "https://",
        ]
        for url in urls:
            with self.subTest(url=url):
                result = factory.keep_url(url=url)
                self.assertTrue(result)
        invalid_urls = ["mailto:info@insta.com", "http://www.example.com/image.png"]
        for url in invalid_urls:
            with self.subTest(url=url):
                result = factory.keep_url(url=url)
                self.assertFalse(result)

    def test_post_proces_url(self):

        factory = InstagramFactory("example")
        # TODO, update test when the full url forumala is discovered
        initial = "https://scontent.cdninstagram.com/v/t51.82787-15/760554696_18615331183007669_4267531026799049042_n.jpg?stp=dst-jpg_e35_s640x640_tt6&_nc_cat=107&ccb=7-5&_nc_sid=18de74&efg=eyJlZmdfdGFnIjoiQ0xJUFMuYmVzdF9pbWFnZV91cmxnZW4uQzMifQ%3D%3D&_nc_ohc=EAQj4ZaTlmMQ7kNvwH1hSLL&_nc_oc=Ado1qNjlPM1ixdYcyY0MiF5fKcTODh-zX_Yuwr-oYesOZdwXlbOAqO_CGunVWboQJFM&_nc_zt=23&_nc_ht=scontent.cdninstagram.com&_nc_gid=eoqmdfGXEIVIxEkUqJUa2g&_nc_ss=7d689&oh=00_AQK0bMW3eSLGiX2lSmdac73S-Zxl0A1DQtJkAHP_Znwu0g&oe=6AA30228"
        expected = "https://scontent.cdninstagram.com/v/t51.82787-15/760554696_18615331183007669_4267531026799049042_n.jpg?stp=dst-jpg_e35_s640x640_tt6&_nc_cat=107&ccb=7-5&_nc_sid=18de74&efg=eyJlZmdfdGFnIjoiQ0xJUFMuYmVzdF9pbWFnZV91cmxnZW4uQzMifQ%3D%3D&_nc_ohc=EAQj4ZaTlmMQ7kNvwH1hSLL&_nc_oc=Ado1qNjlPM1ixdYcyY0MiF5fKcTODh-zX_Yuwr-oYesOZdwXlbOAqO_CGunVWboQJFM&_nc_zt=23&_nc_ht=scontent.cdninstagram.com&_nc_gid=eoqmdfGXEIVIxEkUqJUa2g&_nc_ss=7d689&oh=00_AQK0bMW3eSLGiX2lSmdac73S-Zxl0A1DQtJkAHP_Znwu0g&oe=6AA30228"

        result = factory.post_process_url(initial)
        self.assertEqual(expected, result)
