# /**
# This regex represents a loose rule of an “image candidate string”.

# @see https://html.spec.whatwg.org/multipage/images.html#srcset-attribute

# An “image candidate string” roughly consists of the following:
# 1. Zero or more whitespace characters.
# 2. A non-empty URL that does not start or end with `,`.
# 3. Zero or more whitespace characters.
# 4. An optional “descriptor” that starts with a whitespace character.
# 5. Zero or more whitespace characters.
# 6. Each image candidate string is separated by a `,`.

# We intentionally implement a loose rule here so that we can perform more aggressive error handling and reporting in the below code.
# */
import math
import re
from collections import defaultdict
from dataclasses import dataclass

imageCandidateRegex = re.compile(r"\s*([^,]\S*[^,](?:\s+[^,]+)?)\s*(?:,|$)")


class AllDescriptors(defaultdict):
    def __init__(self, *args, **kwargs):
        self.fallback = False
        super().__init__(*args, **kwargs)


@dataclass
class ImageType:
    def __init__(self, url, width=None, height=None, density=None) -> None:
        self.url = url
        self.width: int | None = width
        self.height: int | None = height
        self.density: int | None = density

    def __lt__(self, other):
        # rules are inconsistent. assume density is highest
        if self.density is not None:
            if other.density is not None:
                return self.density < other.density
            else:
                return True
        if other.density is not None:
            return False
        if self.width is not None:
            if other.width is not None:
                return self.width < other.width
            else:
                return True

        return True


def duplicate_descriptor_check(allDescriptors, value, postfix):
    if allDescriptors[postfix].get(value):
        raise Exception(f"No more than one image candidate is allowed for a given descriptor: {value}{postfix}")
    allDescriptors[postfix][value] = True


def fallback_descriptor_duplicate_check(allDescriptors):
    if allDescriptors.fallback:
        raise Exception("Only one fallback image candidate is allowed")

    if allDescriptors.get("x") and 1 in allDescriptors["x"]:
        raise Exception("A fallback image is equivalent to a 1x descriptor, providing both is invalid.")

    allDescriptors.fallback = True


def descriptor_count_check(allDescriptors, currentDescriptors):
    if len(currentDescriptors) == 0:
        fallback_descriptor_duplicate_check(allDescriptors)
    elif len(currentDescriptors) > 1:
        raise Exception(
            f"Image candidate may have no more than one descriptor, found {len(currentDescriptors)}: {' '.join(map(repr, currentDescriptors))}"
        )


def valid_descriptor_check(value, postfix, descriptor):
    if math.isnan(value):
        raise Exception(f"{descriptor or value} is not a valid number")

    match postfix:
        case "w":
            # Check that the descriptor (minus the 'w') consists only of ASCII digits
            widthString = descriptor[:-1]
            regex = re.compile(r"^\d+$")
            if not regex.match(widthString):
                raise TypeError(f"Width descriptor must be a valid non-negative integer: {descriptor}")

            if value <= 0:
                raise Exception("Width descriptor must be greater than zero")
            elif not isinstance(value, (float, int)):
                raise TypeError("Width descriptor must be an integer")

        case "x":
            # Check that the descriptor (minus the 'x') is a valid floating-point number per HTML spec
            densityString = descriptor[:-1]

            # HTML spec: valid floating-point number cannot be Infinity or NaN
            if math.isinf(value):
                raise TypeError(f"Density descriptor must be a valid floating-point number: {descriptor}")

            # Validate the string format follows HTML floating-point number rules
            # Must be: optional sign, then either (digits + optional decimal + digits) or (decimal + digits), then optional exponent
            regex = re.compile(r"^-?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][+-]?\d+)?$")
            if not regex.match(densityString):
                raise Exception(f"Density descriptor must be a valid floating-point number: {descriptor}")

            if value <= 0:
                raise Exception("Pixel density descriptor must be greater than zero")

        case "h":
            raise Exception("Height descriptor is no longer allowed")

        case _:
            raise Exception(f"Invalid srcset descriptor: {descriptor}")


def parse_src_set(string: str, strict=False):
    allDescriptors = AllDescriptors(dict)

    def foo(part: str):
        parts = part.strip().split()
        url, *descriptors = parts
        result = ImageType(url)
        if strict:
            descriptor_count_check(allDescriptors, descriptors)

        for descriptor in descriptors:
            postfix = descriptor[-1]
            try:
                value = int(descriptor[:-1])
            except ValueError:
                if strict:
                    raise
                value = None
            if strict:
                valid_descriptor_check(value=value, descriptor=descriptor, postfix=postfix)
                duplicate_descriptor_check(allDescriptors=allDescriptors, value=value, postfix=postfix)

            if postfix == "w":
                result.width = value
            elif postfix == "h":
                result.height = value
            elif postfix == "x":
                result.density = value

        return result

    string = re.sub(r"\r?\n", "", string, count=500)
    string = re.sub(r",\s+", ", ", string, count=500)
    x = imageCandidateRegex.split(string)
    # remove the odd matches because those are empty strings
    y = (s for i, s in enumerate(x) if i % 2 == 1)
    return [foo(p) for p in y]


knownDescriptors = {"width": "w", "height": "h", "density": "x"}


def stringify_srcset(array, strict=False):
    allDescriptors = AllDescriptors(dict)

    def foo(element):
        if not hasattr(element, "url"):
            if strict:
                raise Exception("Url is required")
            return ""
        descriptorKeys = [k for k, v in knownDescriptors.items() if getattr(element, k)]

        if strict:
            descriptor_count_check(allDescriptors, descriptorKeys)

        res = [getattr(element, "url")]

        for descriptorKey in descriptorKeys:
            postfix = knownDescriptors.get(descriptorKey)
            value = getattr(element, descriptorKey)

            descriptor = f"{value}{postfix}"
            if strict:
                valid_descriptor_check(value, postfix, descriptor)
                duplicate_descriptor_check(allDescriptors, value, postfix)

            res.append(descriptor)

        return " ".join(res)

    return ", ".join([foo(element) for element in array])
