from unittest import TestCase, mock

from archive import FileSystemMultiArchive


class TestArchive(TestCase):
    def test_non_string(self):

        self.assertRaises(AssertionError, lambda: FileSystemMultiArchive([1]))
        self.assertRaises(AssertionError, lambda: FileSystemMultiArchive(["hello\x01world.txt", "example"]))
        self.assertRaises(AssertionError, lambda: FileSystemMultiArchive(["hello.txt", "", "example.txt"]))

    def test_add_contains(self):


        archive = FileSystemMultiArchive()


        self.assertNotIn("hello",archive)

        archive.add("hello")
        self.assertIn("hello",archive)
