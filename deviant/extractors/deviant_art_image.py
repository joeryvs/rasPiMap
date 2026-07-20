import re

from .image import ImageExtractor


class DeviantArtImageExtractor(ImageExtractor):
    def _regex(self):
        return re.compile(r"^.*/images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/.+$")


class DeviantArtImage2XExtractor(DeviantArtImageExtractor):
    def retrieve_img_src(self, anchor):
        return (x for x in super().retrieve_img_src(anchor) if x.density == 2)


class AllImagesExtractor(DeviantArtImageExtractor):
    def _keep_string(self, regex, string):
        return True


class LargeImageExtractor(DeviantArtImageExtractor):
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
