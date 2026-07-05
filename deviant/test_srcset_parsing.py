import math
import unittest

from srcset_parsing import ImageType, parse_src_set, stringify_srcset


class TestSrcSetParsing(unittest.TestCase):
    def test_white_space(self):
        fixture = " banner-HD.jpeg 2x,    banner-phone.jpeg   100w, http://site.com/image.jpg?foo=bar,lorem 3x ,banner.jpeg    "

        result = parse_src_set(fixture, strict=True)
        expected = [
            ImageType(density=2.0, url="banner-HD.jpeg"),
            ImageType(url="banner-phone.jpeg", width=100.0),
            ImageType(density=3.0, url="http://site.com/image.jpg?foo=bar,lorem"),
            ImageType(url="banner.jpeg"),
        ]
        self.assertListEqual(result, expected)

    def test_parse_with_commas(self):
        fixture = "https://i.kinja-img.com/gawker-media/image/upload/c_fill,f_auto,fl_progressive,g_center,h_180,q_80,w_320/rbx48jwtuvpwum29aarr.jpg 320w, https://i.kinja-img.com/gawker-media/image/upload/c_fill,f_auto,fl_progressive,g_center,h_264,q_80,w_470/rbx48jwtuvpwum29aarr.jpg 470w, https://i.kinja-img.com/gawker-media/image/upload/c_fill,f_auto,fl_progressive,g_center,h_80,q_80,w_80/rbx48jwtuvpwum29aarr.jpg 80w"
        result = parse_src_set(fixture)
        expected = [
            ImageType(
                url="https://i.kinja-img.com/gawker-media/image/upload/c_fill,f_auto,fl_progressive,g_center,h_180,q_80,w_320/rbx48jwtuvpwum29aarr.jpg",
                width=320,
            ),
            ImageType(
                url="https://i.kinja-img.com/gawker-media/image/upload/c_fill,f_auto,fl_progressive,g_center,h_264,q_80,w_470/rbx48jwtuvpwum29aarr.jpg",
                width=470,
            ),
            ImageType(
                url="https://i.kinja-img.com/gawker-media/image/upload/c_fill,f_auto,fl_progressive,g_center,h_80,q_80,w_80/rbx48jwtuvpwum29aarr.jpg",
                width=80,
            ),
        ]
        self.assertListEqual(result, expected)

    def test_parse_if_srcset_seperated_without_whitespaces(self):
        fixture = "banner-HD.jpeg 2x,banner-phone.jpeg 100w,http://site.com/image.jpg?foo=100w,lorem 1x"
        result = parse_src_set(fixture)
        expected = [
            ImageType(url="banner-HD.jpeg", density=2),
            ImageType(url="banner-phone.jpeg", width=100),
            ImageType(url="http://site.com/image.jpg?foo=100w,lorem", density=1),
        ]
        self.assertListEqual(result, expected)

    def test_strict_mode(self):
        expected = [ImageType("images/x.jpg"), ImageType("images/x-retina.jpg", density=2)]

        result = parse_src_set("images/x.jpg, images/x-retina.jpg 2x", strict=True)
        self.assertListEqual(result, expected)

    def test_parse_correctly_with_varied_spacing_and_newlines(self):
        fixture = """image.png,
        					 image@2x.png 2x"""
        expected = [ImageType("image.png"), ImageType(url="image@2x.png", density=2)]
        self.assertListEqual(parse_src_set(fixture), expected)

    def test_stringify_srcset(self):
        fixture = [ImageType("banner-HD.jpeg", density=2), ImageType("banner-phone.jpeg", width=100)]

        result = stringify_srcset(fixture)
        expected = "banner-HD.jpeg 2x, banner-phone.jpeg 100w"
        self.assertEqual(result, expected)

    def test_stringify_srcset_strict_mode(self):
        fixture = [ImageType("banner-HD.jpeg", density=2), ImageType("banner-phone.jpeg", width=100)]

        expected = "banner-HD.jpeg 2x, banner-phone.jpeg 100w"
        self.assertEqual(stringify_srcset(fixture), expected)

    def test_invalid_strings(self):
        invalid_strings = [
            "banner.jpeg, fallback.jpeg",  # Multiple fallback images
            "banner-phone-HD.jpg 100w 2x",  # Multiple descriptors
            "banner-HD.jpeg 2x, banner.jpeg 2x",  # Multiple images with the same descriptor
            "banner-phone.jpeg 100h",  # Height descriptor
            "banner-phone.jpeg 100.1w",  # Non-integer width
            "banner-phone.jpeg -100w",  # Negative width
            "banner-hd.jpeg -2x",  # Negative density
            "banner.jpeg 3q",  # Invalid descriptor
            "banner.jpeg xxx",  # Nonsense descriptor
            "banner.jpg 1x, fallback.jpg",  # Duplicate descriptor because the fallback is equivalent to 1x
            "banner.jpg 2x, other.jpg 2.0x",  # Duplicate descriptors after normalizing
            "banner.jpeg 100abcw",  # Invalid width descriptor with non-digits
            "banner.jpeg 2.5abcx",  # Invalid density descriptor with non-digits
            "banner.jpeg 1.23.45x",  # Invalid density descriptor with multiple decimal points
            "banner.jpeg 5.x",  # Invalid density descriptor with trailing decimal
            "banner.jpeg Infinityx",  # Invalid density descriptor with Infinity
        ]

        for invalid_string in invalid_strings:
            with self.subTest("{string} raises error when parsed in strict mode", string=invalid_string):
                # crashes in strict mode
                self.assertRaises(
                    (TypeError, Exception, ValueError), lambda: parse_src_set(invalid_string, strict=True)
                )
            with self.subTest("{string} doesnt raise error when parsed in non-strict mode", string=invalid_string):
                # no crash in non-strict mode
                result = parse_src_set(invalid_string, strict=False)
                self.assertIsNotNone(result)

    def test_invalid_arrays(self):
        invalid_arrays = [
            [ImageType(url="banner.jpeg"), ImageType(url="fallback.jpeg")],  # Multiple fallback images
            [ImageType(url="banner-phone-HD.jpg", width=100, density=2)],  # Multiple descriptors
            [
                ImageType(url="banner-HD.jpeg", density=2),
                ImageType(url="banner.jpeg", density=2),
            ],  # Multiple images with the same descriptor
            [ImageType(url="banner-phone.jpeg", height=100)],  # Height descriptor
            [ImageType(url="banner-phone.jpeg", width=100.1)],  # Non-integer width
            [ImageType(url="banner-phone.jpeg", width=-100)],  # Negative width
            [ImageType(url="banner-hd.jpeg", density=-2)],  # Negative density
            [ImageType(url="banner.jpeg", width=math.nan)],  # Invalid descriptor
            [ImageType(url="banner.jpeg", width="xxx")],  # Nonsense descriptor
            [
                ImageType(url="banner.jpg", density=1),
                ImageType(url="fallback.jpg"),
            ],  # Duplicate descriptor because the fallback is equivalent to 1x
            [
                ImageType(url="banner-hd.jpg", density=2),
                ImageType(url="other-hd.jpg", density=2),
            ],  # Duplicate descriptors after normalizing
        ]

        for invalid_array in invalid_arrays:
            with self.subTest("{array}stringify_crashes in strict mode", array=invalid_array):
                self.assertRaises(
                    (Exception, TypeError, ValueError), lambda: stringify_srcset(invalid_array, strict=True)
                )
            with self.subTest("{array} stringify_crashes doesnt in non-strict mode", array=invalid_array):
                # no crash in non-strict mode
                result = stringify_srcset(invalid_array, strict=False)
                self.assertIsNotNone(result)


class TestImageTypeOrdering(unittest.TestCase):
    def test_neutral(self):

        a = ImageType("a")
        b = ImageType("b")

        self.assertLess(a, b)
        self.assertLess(b, a)

    def test_density_is_maximum(self):

        a = ImageType("a", density=1)
        b = ImageType("b", width=100)
        c = ImageType("c", width=200)

        maximum = max([a, b, c])

        self.assertIs(maximum, a)

    def test_largest_width(self):
        a = ImageType("a", width=400)
        b = ImageType("b", width=100)
        c = ImageType("c", width=200)

        maximum = max([a, b, c])
        self.assertIs(maximum, a)

    def test_largest_density(self):

        a = ImageType("a", density=4)
        b = ImageType("b", density=1)
        c = ImageType("c", density=2)

        maximum = max([a, b, c])
        self.assertIs(maximum, a)
