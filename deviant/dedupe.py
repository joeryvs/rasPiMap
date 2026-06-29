import argparse

import PIL
from PIL import Image, ImageFile


def keep_largest_image(paths):
    images = [Image.open(path) for path in paths]
    print(images)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input-folder")

    args = parser.parse_args()

    print(args.input_folder)
    print(PIL)
    print(dir(PIL))
    pass


if __name__ == "__main__":
    main()
