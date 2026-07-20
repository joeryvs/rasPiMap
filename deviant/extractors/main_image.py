from .image import ImageExtractor


class MainImageExtractor(ImageExtractor):
    _include_srcset = False

    def _find_elements_kwargs(self):
        MAIN_IMAGE_CLASS = "_Cyjpk"
        return {"class_": MAIN_IMAGE_CLASS}

    def retrieve_img_src(self, anchor):
        return super().retrieve_img_src(anchor)
