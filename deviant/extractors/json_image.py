import json
import logging

from utils import Extractor

_logger = logging.getLogger(__name__)


class JsonImageUrlExtractor(Extractor):
    def extract(self, /, input_path, **kwargs):
        all_urls = self.retrieve(input_path=input_path)
        all_urls = sorted(dict.fromkeys(all_urls))
        self.writer.output_items(all_urls)

    def find_props(self, dictionary, prop):
        result = []

        def find_prop_rec(obj):
            if not obj:
                return
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k == prop:
                        result.append(v)
                    else:
                        find_prop_rec(v)
            if isinstance(obj, list):
                for item in obj:
                    find_prop_rec(item)

        find_prop_rec(dictionary)
        return result

    def construct_url_from_media(self, media):
        baseUri: str = media.get("baseUri")
        prettyName: str = media.get("prettyName")
        tokens: list[str] = media.get("token")
        # if baseUri is None:
        #     _logger.error("current media has no baseUri: %s", media)
        # if prettyName is None:
        #     _logger.error("current media has no prettyName: %s", media)
        if not tokens:
            _logger.warning("No tokens available for %s, %s", prettyName, baseUri)
        token = "?token=" + tokens[0] if tokens else ""
        types: list[dict] = media.get("types")

        fullviews = [t for x in self._image_size_order() for t in types if t.get("t") == x]
        if fullviews:
            fullview = fullviews[0]
            c = fullview.get("c") or ""
            extension = c.replace("<prettyName>", prettyName)
            url = baseUri + extension + token
            _logger.debug("URL for %s is %s", prettyName, url)
            return url
        else:
            _logger.info("No fullviews for %s, %s", prettyName, baseUri)
        return ""

    def _image_size_order(self) -> list[str]:
        # t is fullview or pre or social_preview
        # find first fullview, then preview and social_preview as backups
        return ["fullview", "preview", "social_preview"]

    def retrieve(self, input_path):
        a = self.find_elements(input_path, "script", id="_R_")
        for b in a:
            text = b.text
            lines = text.split("\n")
            important: str = lines[3]
            # make a lot of assumption no of the structure
            important = important.removeprefix("window.__INITIAL_STATE__ = JSON.parse(").removesuffix(");")
            # kinda dangeroues to run arbartraty code,
            important = eval(important, {}, {})
            x = json.loads(important)
            _logger.debug("evaluated line of %s", x)
            # find all "media"
            medias = self.find_props(x, "media")
            # construct url
            urls = [self.construct_url_from_media(media) for media in medias]
            yield from urls


class JsonImagePreUrlExtractor(JsonImageUrlExtractor):
    def _image_size_order(self) -> list[str]:
        # preview is the one that is guaranteed to be not to large
        return ["preview"]
