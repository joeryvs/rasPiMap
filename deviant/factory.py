#!../venv/bin/python
import logging

from deviant.webscrape_extractors import (
    AllImagesExtractor,
    AllPagesExtractor,
    ArtPageExtractor,
    AvatarExtractor,
    DescriptionExtractor,
    DeviantArtImage2XExtractor,
    DeviantArtImageExtractor,
    Extractor,
    HighestUserExtractor,
    JsonExtractor,
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
