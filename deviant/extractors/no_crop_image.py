import logging

from .deviant_art_image import DeviantArtImageExtractor

_logger = logging.getLogger(__name__)


class NoCropImageExtractor(DeviantArtImageExtractor):
    def _keep_string(self, regex, string):
        return super()._keep_string(regex, string) and "/crop/" not in string


class NoCropImageExtractorLarge(NoCropImageExtractor):
    _include_srcset = True

    def retrieve_img_src(self, anchor):
        result = super().retrieve_img_src(anchor)

        maximum = max(result, default=None)
        if maximum:
            _logger.debug("maximum is %s", maximum)
            yield maximum
