import builtins
import unittest
import unittest.mock
from collections.abc import Generator

from utils import (
    find_key_rec,
    find_key_rec_with_path,
    find_keys_rec,
    find_keys_rec_without_path,
    print_iter_item,
    unique,
)


class TestUtils(unittest.TestCase):
    def test_find_key_rec(self):

        a = {"a": {"b": "c", "d": "e"}, "f": ["g", {"h": ["i", {"j": "k"}]}]}

        result = find_key_rec(a, "j")

        self.assertEqual(find_key_rec(a, "j"), "k")
        self.assertIsNone(find_key_rec(a, "k"))
        self.assertEqual(find_key_rec(a, "a"), {"b": "c", "d": "e"})

        self.assertRaises(AssertionError,lambda: find_key_rec(a, 0))

    def test_print_iter_item(self):

        sequence = [1, 2, 3, 4, 1, 2, 3, 4]

        with unittest.mock.patch("builtins.open") as mock_open, unittest.mock.patch("builtins.print") as mock_print:
            result = print_iter_item("test_file.tmp", sequence)
            self.assertIsInstance(result, Generator)
            mock_open.assert_not_called()
            mock_print.assert_not_called()

            res = iter(result)
            mock_open.assert_not_called()
            mock_print.assert_not_called()
            self.assertEqual(next(res), 1)
            mock_print.assert_called_once()
            mock_open.assert_called_once_with("test_file.tmp", "a")

            results = list(result)

            self.assertListEqual(results, [2, 3, 4, 1, 2, 3, 4])
            mock_open.assert_called_once()
            self.assertEqual(8, mock_print.call_count)

    def test_unique(self):

        sequence = [1, 1, 1, 2, 3, 4, 5, 1, 3, 4, 2, 5, 3, 2, 1, 4, 2, 3]

        result = unique(sequence)

        self.assertIsInstance(result, Generator)

        result = list(result)

        self.assertListEqual(result, [1, 2, 3, 4, 5])
