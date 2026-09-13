#!../venv/bin/python
import logging

from extractors import (
    AllPagesExtractor,
    ArtPageExtractor,
    AvatarExtractor,
    DefaultImageExtractor,
    DescriptionExtractor,
    DeviantArtAllImagesExtractor,
    DeviantArtImage2XExtractor,
    DeviantArtImageExtractor,
    DeviantArtLargeImageExtractor,
    HighestUserExtractor,
    ImageExtractor,
    JsonAdditionalMediaExtractor,
    JsonExtractor,
    JsonImagePermutationExtractor,
    JsonImagePreUrlExtractor,
    JsonImagePreUrlNoBlurExtractor,
    JsonImageUrlExtractor,
    JsonLiteratureUrl,
    JsonPdfExtractor,
    JsonVideoAllExtractor,
    JsonVideoBestExtractor,
    LargestImageExtractor,
    LinkExtractor,
    MainImageExtractor,
    NoCropImageExtractor,
    NoCropImageExtractorLarge,
    PageExtractor,
    StoryExtractor,
    TagPageExtractor,
    UserPageExtractor,
    VideoExtractor,
)
from utils import Extractor

_logger = logging.getLogger(__name__)


class ExtractorFactory:
    def __init__(self):
        self._options = {
            "art": ArtPageExtractor,
            "image": ImageExtractor,
            "default_image": DefaultImageExtractor,
            "largest_image": LargestImageExtractor,
            "deviantart.image": DeviantArtImageExtractor,
            "deviantart.image2x": DeviantArtImage2XExtractor,
            "deviantart.large_image": DeviantArtLargeImageExtractor,
            "no_crop": NoCropImageExtractor,
            "no_crop_large": NoCropImageExtractorLarge,
            "deviantart.all_images": DeviantArtAllImagesExtractor,
            "deviantart.main_image": MainImageExtractor,
            "deviantart.avatar": AvatarExtractor,
            "users": UserPageExtractor,
            "highest_user_page_number": HighestUserExtractor,
            "all_links": AllPagesExtractor,
            "tags": TagPageExtractor,
            "deviantart.description": DescriptionExtractor,
            "deviantart.story": StoryExtractor,
            "json": JsonExtractor,
            "json_art": JsonImageUrlExtractor,
            "deviantart.additionalmedia": JsonAdditionalMediaExtractor,
            "json_perm": JsonImagePermutationExtractor,
            "json_video": JsonVideoAllExtractor,
            "json_video_best": JsonVideoBestExtractor,
            "json_pdf": JsonPdfExtractor,
            "json_literature_url": JsonLiteratureUrl,
            "json_art_pre": JsonImagePreUrlExtractor,
            "deviantart.json.pre.noblur": JsonImagePreUrlNoBlurExtractor,
            "video": VideoExtractor,
            "link": LinkExtractor,
        }

        # test the keys.
        for k, v in self._options.items():
            assert k == v._name, "%s is not %s in %s" % (k, v._name, v.__name__)

    @property
    def choices(self):
        return list(self._options.keys())

    def extractor(self, item, *args, **kwargs) -> Extractor:
        return self._options[item](*args, **kwargs)
