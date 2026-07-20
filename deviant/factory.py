#!../venv/bin/python
import logging

# from deviant.extractors.art_page import ArtPageExtractor
# from deviant.extractors.avatar import AvatarExtractor
# from deviant.extractors.description import DescriptionExtractor
# from deviant.extractors.deviant_art_image import AllImagesExtractor, DeviantArtImage2XExtractor, DeviantArtImageExtractor, LargeImageExtractor
# from deviant.extractors.highest_user import HighestUserExtractor
# from deviant.extractors.json import JsonExtractor
# from deviant.extractors.json_image import JsonImageUrlExtractor
# from deviant.extractors.main_image import MainImageExtractor
# from deviant.extractors.no_crop_image import NoCropImageExtractor, NoCropImageExtractorLarge
# from deviant.extractors.page import AllPagesExtractor, ArtPageExtractor, TagPageExtractor, UserPageExtractor
# from deviant.extractors.story import StoryExtractor
# from deviant.utils import Extractor
from .extractors import (
    AllImagesExtractor,
    AllPagesExtractor,
    ArtPageExtractor,
    AvatarExtractor,
    DescriptionExtractor,
    DeviantArtImage2XExtractor,
    DeviantArtImageExtractor,
    HighestUserExtractor,
    JsonImageUrlExtractor,
    LargeImageExtractor,
    MainImageExtractor,
    NoCropImageExtractor,
    NoCropImageExtractorLarge,
    StoryExtractor,
    TagPageExtractor,
    UserPageExtractor,
)

_logger = logging.getLogger(__name__)


class ExtractorFactory:
    def __init__(self):
        self._options = {
            "art": ArtPageExtractor,
            "images": DeviantArtImageExtractor,
            "images2x": DeviantArtImage2XExtractor,
            "large_images": LargeImageExtractor,
            "no_crop": NoCropImageExtractor,
            "no_crop_large": NoCropImageExtractorLarge,
            "all_images": AllImagesExtractor,
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
        }

    @property
    def choices(self):
        return list(self._options.keys())

    def extractor(self, item, *args, **kwargs) -> Extractor:
        return self._options[item](*args, **kwargs)
