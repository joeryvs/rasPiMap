#!../venv/bin/python
import argparse
import pathlib

from webscrape_extractors import ExtractorFactory


def main():
    path = pathlib.Path(__file__).parent / "index.html"
    output = pathlib.Path(__file__).parent / "art_links.txt"

    factory = ExtractorFactory()
    parser = argparse.ArgumentParser(
        prog="webscrape_dev",
        description="Choose mode and other options",
        epilog="hello world",
    )

    parser.add_argument("type", choices=factory.choices)
    parser.add_argument("-i", "--input", default=path, nargs="+")
    parser.add_argument("-o", "--output", default=output, nargs="?")

    args = parser.parse_args()
    print(args.type)
    print(args.input)
    print(args.output)

    extractor_object = factory.extractor(args.type)
    if extractor_object:
        extractor_object.extract(args.input, args.output)


if __name__ == "__main__":
    main()
