import re

from .image import ImageExtractor


class AvatarExtractor(ImageExtractor):
    _name = "deviantart.avatar"
    def _regex(self):
        return re.compile(r"^https://a.deviantart.net/.*$")
