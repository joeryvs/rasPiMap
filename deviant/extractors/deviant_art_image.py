import re

from .image import ImageExtractor


class DeviantArtImageExtractor(ImageExtractor):
    _name = "deviantart.image"
    def _regex(self):
        return re.compile(r"^.*/images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/.+$")


class DeviantArtImage2XExtractor(DeviantArtImageExtractor):
    _name = "deviantart.image2x"
    def retrieve_img_src(self, anchor):
        return (x for x in super().retrieve_img_src(anchor) if x.density == 2)


class DeviantArtAllImagesExtractor(DeviantArtImageExtractor):
    _name = "deviantart.all_images"
    def _keep_string(self, regex, string):
        return True


class DeviantArtLargeImageExtractor(DeviantArtImageExtractor):
    _name = "deviantart.large_image"
    def _regex(self):
        return re.compile(
            r"^.*/images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/\w/(\d|\w|\-)+/(\d|\w|\-|\.)+\?token=(.*)$"
        )

    # def _keep_string(self, regex, string):
    #     return (
    #         super().keep_string(regex, string)
    #         and "/crop/" not in string
    #         and "/fit/" not in string
    #         and "/fill/" not in string
    #     )
