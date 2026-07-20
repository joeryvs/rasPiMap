import re

from .image import ImageExtractor


class AvatarExtractor(ImageExtractor):
    def _regex(self):
        return re.compile(r"^https://a.deviantart.net/.*$")
