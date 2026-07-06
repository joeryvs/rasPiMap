#!../venv/bin/python
import argparse
import pathlib

from webscrape_extractors import ExtractorFactory


def main():

    factory = ExtractorFactory()
    parser = argparse.ArgumentParser(
        prog="webscrape_dev",
        description="Choose mode and other options",
        epilog="hello world",
    )

    parser.add_argument("type", choices=factory.choices)
    parser.add_argument("-i", "--input", nargs="+")
    parser.add_argument("-o", "--output")

    args = parser.parse_args()
    print(args.type)
    print(args.input)
    print(args.output)

    extractor_object = factory.extractor(args.type)
    if extractor_object:
        extractor_object.extract(args.input, args.output)


if __name__ == "__main__":
    main()
