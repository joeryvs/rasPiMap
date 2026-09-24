from unittest import TestCase, mock

from combine_scrape import FACTORIES


class TestFactories(TestCase):
    def test_combine_scrape_factory_creating_with_user(self):

        valid_users = ["tom", "foo-", "mr_beast"]

        for key, factory in FACTORIES.items():
            with self.subTest(key=key, factory=factory):
                for user in valid_users:
                    with self.subTest(username=user):
                        result = factory(user)
                        self.assertIsNotNone(result)
