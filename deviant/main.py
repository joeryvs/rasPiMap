#!../venv/bin/python
import argparse
import logging

from factory import ExtractorFactory
from utils import FileWriter, Reader, StdoutWriter


def get_arguments(choices: list[str]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="webscrape_dev",
        description="Choose mode and other options",
        epilog="hello world",
    )

    parser.add_argument("type", choices=choices)
    parser.add_argument("-i", "--input-path", nargs="+")
    parser.add_argument("-o", "--output-path", default="-")

    parser.add_argument("--sort", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--unique", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--verbose", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--log-level", choices=list(logging._levelToName.values()), default="INFO")

    parser.add_argument_group()

    return parser


def main():

    factory = ExtractorFactory()

    parser = get_arguments(factory.choices)
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)
    if not args.quiet:
        for k, v in vars(args).items():
            print(k, v)
    reader = Reader()
    writer = StdoutWriter() if args.output_path == "-" else FileWriter(args.output_path)
    extractor_object = factory.extractor(args.type, reader, writer)
    if extractor_object:
        extractor_object.extract(**vars(args))


if __name__ == "__main__":
    main()
