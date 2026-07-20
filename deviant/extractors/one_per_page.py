import logging
import os
import pathlib
import sys
from abc import ABC, abstractmethod

from bs4 import BeautifulSoup

from deviant.utils import Extractor

_logger = logging.getLogger(__name__)


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
