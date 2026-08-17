import argparse
import logging
import os
import subprocess
import sys

from database import create_db, fill_with_json_data, update_file_times
from extractors import (
    ArtPageExtractor,
    DescriptionExtractor,
    HighestUserExtractor,
    JsonExtractor,
    JsonImagePreUrlExtractor,
    MainImageExtractor,
    StoryExtractor,
    TagPageExtractor,
)
from utils import FileWriter, IOWriter, Reader

VERSION = "1.0"
_logger = logging.getLogger(__name__)


def wget_download(input_file: str, directory_prefix: str, wait_time: float, check: bool = True):
    # Download the image with wget
    rejected_log = "rejected_log.log"
    open(rejected_log, "a").close()
    cmd = ["wget", "--input-file", input_file, "--directory-prefix", directory_prefix]
    if wait_time:
        cmd.extend(["--wait", str(wait_time), "--random-wait"])

    cmd.extend(["--no-verbose", "--rejected-log", rejected_log])
    try:
        p = subprocess.run(cmd, stdout=sys.stdout, stderr=sys.stderr, check=check)
        _logger.info("Process %s, end with code %s", p.args, p.returncode)
    except subprocess.CalledProcessError as e:
        _logger.error("Process %s Error with code %s", e.args, e.returncode)


def run(
    user: str,
    /,
    wait_pages: float,
    wait_images: float,
    skip_gallary_download: bool,
    skip_pages_download: bool,
    skip_image_download: bool,
    download_from_gallary: bool,
    post_process: bool,
):
    _logger.info("running process for %s", user)
    _logger.info(
        "skip gallary : %s, skip pages : %s, download from gallary %s, skip image : %s, post process %s",
        skip_gallary_download,
        skip_pages_download,
        download_from_gallary,
        skip_image_download,
        post_process,
    )
    _logger.info("Wait time page %s, Wait time image %s", wait_pages, wait_images)

    reader = Reader()
    gal_page = f"{user}_gal_page_1.html"
    if not skip_gallary_download:
        # Download gallary
        subprocess.run(["./user_page1_scrape.sh", user], check=True)
        writer = IOWriter()
        HighestUserExtractor(reader=reader, writer=writer).extract(input_path=gal_page)  # pyright: ignore[reportUnknownMemberType]
        str_buffer = writer.get_buffer
        AMOUNT = str(int(str_buffer.getvalue()))
        _logger.info("Downloading %s gallary pages for %s", AMOUNT, user)
        subprocess.run(["gallary-pages/scrape_user.sh", user, AMOUNT], check=True)
    gal_pages = f"gallary-pages/{user}/"
    if download_from_gallary:
        json_pre_image = f"{user}_json_pre_image.txt"
        JsonImagePreUrlExtractor(reader=reader, writer=FileWriter(json_pre_image)).extract(
            gal_pages, sort=True, unique=True
        )
        dir_pre = f"{user}_pre"
        wget_download(input_file=json_pre_image, directory_prefix=dir_pre, wait_time=wait_images)
        # remove the query parameter
        _ = subprocess.run(["../remove_post.sh", dir_pre], check=True, capture_output=True)
        # Extract JSON from GAllARY
        dir_json_gal = f"{user}_gal_json"
        JsonExtractor(reader=reader, writer=FileWriter(dir_json_gal)).extract(input_path=gal_pages)

        if post_process:
            user_gal_db = f"{user}_gal.sqlite"
            db = create_db(user_gal_db)

            fill_with_json_data(db, dir_json_gal, dry_run=False, max_depth=1)
            # update the time stamps on story/description/json and image
            for p in [dir_pre]:
                if os.path.isdir(p):
                    update_file_times(db, p, dry_run=False)
        return

    art_pages_link_file = f"{user}_art.txt"
    art_pages = f"Art-Pages/{user}_art/"
    if not skip_pages_download:
        # subprocess.run(["python", "main.py", "art", "-i", gal_pages, "-o", art_pages_link_file, "--quiet"], check=True)
        ArtPageExtractor(reader=reader, writer=FileWriter(art_pages_link_file)).extract(
            gal_pages, sort=True, unique=True
        )

        wget_download(input_file=art_pages_link_file, directory_prefix=art_pages, wait_time=wait_pages)
    dir_desc = f"{user}_desc"
    dir_story = f"{user}_story"
    dir_json = f"{user}_json"
    dir_main = f"{user}_main"
    main_image = f"{user}_main_image.txt"
    if not skip_image_download:
        # find image links
        MainImageExtractor(reader=reader, writer=FileWriter(main_image)).extract(
            input_path=art_pages, sort=True, unique=True
        )

        # output description/story/json description
        DescriptionExtractor(reader=reader, writer=FileWriter(dir_desc)).extract(input_path=art_pages)
        JsonExtractor(reader=reader, writer=FileWriter(dir_json)).extract(input_path=art_pages)
        StoryExtractor(reader=reader, writer=FileWriter(dir_story)).extract(input_path=art_pages)
        TagPageExtractor(reader=reader, writer=FileWriter(f"{user}_tag.txt")).extract(input_path=art_pages)
        ArtPageExtractor(reader=reader, writer=FileWriter(f"{user}_outgoing_art.txt")).extract(input_path=art_pages)
        # Download the image with wget

        wget_download(input_file=main_image, directory_prefix=dir_main, wait_time=wait_images)

        # remove the query parameter
        _ = subprocess.run(["../remove_post.sh", dir_main], check=True, capture_output=True)

    user_db = f"{user}.sqlite"
    if post_process:
        db = create_db(user_db)

        fill_with_json_data(db, dir_json, dry_run=False, max_depth=1)
        # update the time stamps on story/description/json and image
        for p in [dir_desc, dir_story, dir_main, dir_json]:
            if os.path.isdir(p):
                update_file_times(db, p, dry_run=False)


def main():

    logging.basicConfig(level="DEBUG")
    parser = argparse.ArgumentParser()

    parser.add_argument("user", type=str)
    parser.add_argument("--skip-gallary-download", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--skip-pages-download", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--skip-image-download", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--download-from-gallary", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--post-process", action=argparse.BooleanOptionalAction, default=False)

    parser.add_argument("--wait-pages", type=float, default=6.0)
    parser.add_argument("--wait-images", type=float, default=3.0)
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {VERSION}")

    args = parser.parse_args()

    run(
        args.user,
        wait_pages=args.wait_pages,
        wait_images=args.wait_images,
        skip_gallary_download=args.skip_gallary_download,
        skip_pages_download=args.skip_pages_download,
        skip_image_download=args.skip_image_download,
        download_from_gallary=args.download_from_gallary,
        post_process=args.post_process,
    )


if __name__ == "__main__":
    main()
