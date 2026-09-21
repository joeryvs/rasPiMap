import json
import logging
import os
import pathlib
import sys
from collections.abc import Iterable

import esprima
from bs4 import BeautifulSoup
from utils import Extractor

_logger = logging.getLogger(__name__)


class JsonExtractor(Extractor):
    _name = "json"

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
        for name in input_path:
            _logger.debug("Start parsing %s", name)
            if not name.exists():
                _logger.error("ERROR %s file does not exist", name)
                continue
            with open(name, "r", encoding=sys.getfilesystemencoding()) as f:
                soup = BeautifulSoup(f.read(), features="html.parser")
            script = soup.find("script", id="_R_")
            if not script:
                _logger.error("ERROR %s file has no _R_ script section", name)
                continue
            text = script.text
            parsed_script = esprima.parseScript(text)

            # make a lot of assumption no of the structure
            important = parsed_script.body[2].expression.right.arguments[0].value
            new_important = important
            # parse to obj and back to string
            try:
                # prettify the JSON, by loading and dumping
                json_content = json.loads(new_important)
                output = json.dumps(
                    json_content,
                    check_circular=True,
                    allow_nan=False,
                    ensure_ascii=True,
                    sort_keys=True,
                    indent=2,
                )
            except json.decoder.JSONDecodeError:
                _logger.error("ERROR %s has an imparseble json content", name)
                output = important
            except TypeError as te:
                _logger.error("ERROR %s has a TypeError %s", name, te)
                output = important
            name = name.with_suffix(".json").name
            self.writer.output_content_to_directory(name, output)

    def retrieve(self, input_path) -> Iterable:
        return super().retrieve(input_path)
