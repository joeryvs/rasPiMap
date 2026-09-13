import logging

import extractors
from utils import Extractor

_logger = logging.getLogger(__name__)


class ExtractorFactory:
    def __init__(self):

        # Build a dictionary of options from the extractors module
        self._options = {}
        for a in extractors.__all__:
            extractor = getattr(extractors, a)
            if name := getattr(extractor, "_name", None):
                if name in self._options:
                    raise ValueError(f"name {name} is double defined")
                self._options[name] = extractor

        # test the keys.
        for k, v in self._options.items():
            assert k == v._name, "%s is not %s in %s" % (k, v._name, v.__name__)

    @property
    def choices(self):
        return list(self._options.keys())

    def extractor(self, item, *args, **kwargs) -> Extractor:
        return self._options[item](*args, **kwargs)
