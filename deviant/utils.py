import io
import logging
import os
import pathlib
import sys
from abc import ABC, abstractmethod
from collections.abc import Iterable

from bs4 import BeautifulSoup

_logger = logging.getLogger(__name__)


class Reader:
    def find_elements(self, path, elm_name, **kwargs):
        if isinstance(path, (str, pathlib.Path, bytes)):
            path = [path]
        for p in path:
            p = pathlib.Path(p)
            if p.is_dir():
                _logger.debug("Recursive on %s", p)
                yield from self.find_elements(path=(p / n for n in os.listdir(p)), elm_name=elm_name, **kwargs)
            elif p.is_file():
                _logger.debug("Parsing %s", p)
                with open(p, "r") as f:
                    data = f.read()
                soup = BeautifulSoup(data, features="html.parser")
                yield from soup.find_all(name=elm_name, **kwargs)
            else:
                _logger.error("%s IS NOT A FILE", p)


class Writer(ABC):
    @abstractmethod
    def output_items(self, items):
        pass

    @abstractmethod
    def output_content_to_directory(self, name, content):
        pass


class StdoutWriter(Writer):
    def __init__(self) -> None:
        super().__init__()

    def output_items(self, items):
        for p in items:
            print(p)

    def output_content_to_directory(self, name, content):
        print("##", name)
        print(content)
        return super().output_content_to_directory(name, content)


class FileWriter(Writer):
    def __init__(self, output) -> None:
        self.output_file = pathlib.Path(output)
        super().__init__()

    def output_items(self, items):

        with open(self.output_file, "w") as f:
            for i in items:
                print(i, file=f)

    def output_content_to_directory(self, name, content):
        path = self.output_file / name
        os.makedirs(self.output_file, exist_ok=True)
        with open(path, "w", encoding=sys.getfilesystemencoding()) as f:
            print(content, file=f)


class IOWriter(Writer):
    def __init__(self) -> None:
        self.buffer = io.StringIO()
        super().__init__()

    def output_items(self, items):
        for i in items:
            print(i, file=self.buffer)

    def output_content_to_directory(self, name, content):
        print("##", name, file=self.buffer)
        print(content, file=self.buffer)
        return super().output_content_to_directory(name, content)

    @property
    def get_buffer(self):
        return self.buffer


class Extractor(ABC):
    def __init__(self, reader: Reader, writer: Writer):
        self.reader = reader
        self.writer = writer

    def find_elements(self, path, elm_name, **kwargs):
        return self.reader.find_elements(path, elm_name, **kwargs)

    @abstractmethod
    def extract(self, /, input_path, **kwargs) -> None:
        pass

    @abstractmethod
    def retrieve(self, input_path) -> Iterable:
        return []

class OnePerPageExtractor(Extractor, ABC):
    def extract(self, /, input_path, **kwargs):
        if not isinstance(input_path, list):
            input_path = [input_path]

        input_path = [
            y
            for i in input_path
            for ys in [[pathlib.Path(i) / z for z in os.listdir(i)] if pathlib.Path(i).is_dir() else [pathlib.Path(i)]]
            for y in ys
            if y.is_file()
        ]
        for input in input_path:
            if not input.exists():
                _logger.error("ERROR %s file does not exist", input)
                continue
            with open(input, "r", encoding=sys.getfilesystemencoding()) as f:
                soup = BeautifulSoup(f.read(), features="html.parser")

            self.handle_page(input, soup)

    @abstractmethod
    def handle_page(self, name, soup):
        pass

    def retrieve(self, input_path):
        return super().retrieve(input_path)
