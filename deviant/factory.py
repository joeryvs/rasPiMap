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
    JsonExtractor,
    JsonImagePermutationExtractor,
    JsonImagePreUrlExtractor,
    JsonImageUrlExtractor,
    LargestImageExtractor,
    MainImageExtractor,
    NoCropImageExtractor,
    NoCropImageExtractorLarge,
    PageExtractor,
    StoryExtractor,
    TagPageExtractor,
    UserPageExtractor,
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
            "deviantart_images": DeviantArtImageExtractor,
            "deviantart_images2x": DeviantArtImage2XExtractor,
            "deviantart_large_images": DeviantArtLargeImageExtractor,
            "no_crop": NoCropImageExtractor,
            "no_crop_large": NoCropImageExtractorLarge,
            "deviant_art_all_images": DeviantArtAllImagesExtractor,
            "main_image": MainImageExtractor,
            "avatar": AvatarExtractor,
            "users": UserPageExtractor,
            "highest_user_page_number": HighestUserExtractor,
            "all_links": AllPagesExtractor,
            "tags": TagPageExtractor,
            "description": DescriptionExtractor,
            "story": StoryExtractor,
            "json": JsonExtractor,
            "json_art": JsonImageUrlExtractor,
            "json_perm": JsonImagePermutationExtractor,
            "json_art_pre": JsonImagePreUrlExtractor,
        }

    @property
    def choices(self):
        return list(self._options.keys())

    def extractor(self, item, *args, **kwargs) -> Extractor:
        return self._options[item](*args, **kwargs)
