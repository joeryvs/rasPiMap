import os
from collections.abc import Iterable
from dataclasses import dataclass


@dataclass
class FileWrapper:
    filename: str
    stat_result: os.stat_result | None


class FileSystemMultiArchive:
    def __init__(self, files=None) -> None:
        if files is None:
            files = []
        self.files: list[FileWrapper] = [FileWrapper(file, None) for file in files]
        assert all(isinstance(file.filename, str) for file in self.files)
        assert all(file.filename for file in self.files)
        assert all(file.filename.isprintable() for file in self.files)
        self._loaded = False
        self.items = set()

    def __contains__(self, item):
        if not self._loaded:
            self.load()

        if item in self.items:
            return True
        for file_info in self.files:
            filename = file_info.filename
            old_stat_result = file_info.stat_result
            if not os.path.isfile(filename):
                continue

            current_stat_result = os.stat(filename)
            # If the
            if old_stat_result is None or current_stat_result.st_ctime_ns > old_stat_result.st_ctime_ns:
                _, sr, lines = self._read_file(file=filename)
                self.items.update(lines)
                file_info.stat_result = sr
                if item in lines:
                    return True
        return False

    def add(self, item: str):
        # Verify information about the item that is intended to be added to our archive
        assert isinstance(item, str), "line is not a string"
        assert item, "line is empty"
        assert item.isprintable(), "line is not printable"
        assert "\n" not in item, "line contains new-line character"
        if not self._loaded:
            self.load()
        # for every file, append the newline
        for file in self.files:
            with open(file.filename, mode="a") as f:
                print(item, file=f)
        self.items.add(item)

    def load(self):
        if self._loaded:
            return

        for i, file_wrapper in enumerate(self.files):
            # Read the file, save last access information and current lines, and add lines to set
            if os.path.isfile(file_wrapper.filename):
                _, stat_result, lines = self._read_file(file=file_wrapper.filename)
                file_wrapper.stat_result = stat_result
                self.items.update(lines)
        self._loaded = True

    def _read_file(self, file: str):
        if os.path.isfile(file):
            res = os.stat(file)
            with open(file=file, mode="r") as fp:
                lines = fp.readlines()
            lines = [line.strip() for line in lines]
        else:
            res = None
            lines = []
        return file, res, lines
