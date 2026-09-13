import logging
import os
import time

from archive import FileSystemMultiArchive
from extractors import JsonLiteratureUrl
from utils import FileWriter, Reader
from wget_utils import download_file, download_from_stream

_logger = logging.getLogger(__name__)


def run(
    *,
    url: str | None,
    archive: FileSystemMultiArchive,
    max_downloads: int,
    html_dir: str,
    wait_time: float,
    continuation_archive,
):
    stack = []
    if os.path.exists(continuation_archive):
        with open(continuation_archive, mode="r") as f:
            for line in f:
                stack.append(line.strip())
    if url:
        stack.append(url.strip())
    try:
        counter = 0
        r = Reader()
        w = FileWriter("example.log")
        extractor = JsonLiteratureUrl(r, w)
        while stack:
            if counter > max_downloads:
                break
            # Peek the last element of the stack
            current_url = stack[-1]
            if current_url in archive:
                assert stack.pop() == current_url
                _logger.info("Skipping %s", current_url)
                continue
            counter += 1
            current_file_name = download_file(current_url, out=html_dir, update_write_time=True)
            # Remove top of stack before adding new elements
            assert stack.pop() == current_url
            stack.extend(extractor.retrieve(current_file_name))
            archive.add(current_url)
            _logger.info("Counter: %s, stack length: %s", counter, len(stack))
            time.sleep(wait_time)
    finally:
        _logger.info("%s Remaining urls", len(stack))
        if continuation_archive:
            with open(continuation_archive, "w") as f:
                print(*stack, sep="\n",file=f)


def main():
    from argparse import ArgumentParser, BooleanOptionalAction

    parser = ArgumentParser()

    parser.add_argument("-a", "--download-archive", nargs="*")
    parser.add_argument("--max-downloads", type=int)
    parser.add_argument("--html-dir", required=True)
    parser.add_argument("--wait", required=True, default=8, type=float)
    parser.add_argument("--continuation-archive")
    parser.add_argument("STORY_URL", default=None)

    args = parser.parse_args()
    logging.basicConfig(level="DEBUG")

    download_archive = args.download_archive
    max_downloads = args.max_downloads
    html_dir = args.html_dir
    wait_time = args.wait
    continuation_archive = args.continuation_archive
    url = args.STORY_URL
    assert isinstance(max_downloads, int) and max_downloads >= 0
    assert isinstance(wait_time, float) and wait_time >= 0
    archive = FileSystemMultiArchive(download_archive)
    os.makedirs(html_dir, exist_ok=True)
    _logger.info("Arguments parsed and prepared, beginning run function")
    run(
        url=url,
        archive=archive,
        max_downloads=max_downloads,
        html_dir=html_dir,
        wait_time=wait_time,
        continuation_archive=continuation_archive,
    )


if __name__ == "__main__":
    main()
