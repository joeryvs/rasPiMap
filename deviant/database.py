import argparse
import datetime
import json
import logging
import os
import pathlib
import sqlite3
from collections.abc import Generator

_logger = logging.getLogger(__name__)


def create_db(database) -> sqlite3.Connection:

    con = sqlite3.connect(database)

    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS image(
        entityID TEXT NOT NULL ON CONFLICT FAIL UNIQUE ON CONFLICT IGNORE,
        publishedDate TEXT NOT NULL ON CONFLICT FAIL,
        media TEXT,
        baseUri TEXT,
        prettyName TEXT,
        hasBlockReasons INTEGER,
        shortUrl TEXT NOT NULL,
        url TEXT NOT NULL,
        pageTitle TEXT NOT NULL,
        title TEXT NOT NULL
    ) STRICT
    """)
    cur.execute("""CREATE TABLE IF NOT EXISTS token(
        entityID TEXT REFERENCES images (entityID) ON DELETE CASCADE NOT NULL,
        token TEXT NOT NULL,
        CONSTRAINT entity_token_unique UNIQUE(entityID, token) ON CONFLICT IGNORE,
        CONSTRAINT entity_reference_image FOREIGN KEY (entityID) REFERENCES image ON DELETE CASCADE
        ) STRICT
        """)
    cur.execute("""CREATE TABLE IF NOT EXISTS imageSize(
        entityID TEXT REFERENCES images (entityID) ON DELETE CASCADE NOT NULL,
        WIDTH INTEGER NOT NULL CHECK (WIDTH >= 0),
        HEIGHT INTEGER NOT NULL CHECK (HEIGHT >= 0),
        TYPE TEXT NOT NULL,
        COMPONENT TEXT,
        FILENAME TEXT,
        RADIUS INTEGER NOT NULL,
        CONSTRAINT entityID_width_height_unique UNIQUE(entityID,Width,Height,type,filename) ON CONFLICT IGNORE
        ) STRICT
        """)
    con.commit()
    return con


def update_file_times(db: sqlite3.Connection, directory_path, dry_run=False):
    rd = find_image_upload_data(db, directory_path)
    for path, create_time in rd:
        if create_time is None:
            _logger.warning("No time found for %s", path)
        else:
            _logger.info("%s will be updated to %s", path, create_time)
            if not dry_run:
                os.utime(path=path, times=(create_time, create_time))


def find_image_publish_date(cur: sqlite3.Connection, image_file_name) -> None | float:
    # TODO, USE 1 QUERY with a join statement
    # t2 = cur.execute(
    #     """SELECT im.publishedDate, im.title,isize.width,isize.height,isize.entityID,im.entityID FROM image AS im
    #         RIGHT JOIN imageSize AS isize ON isize.entityID = im.entityID
    #         WHERE
    #         isize.FILENAME = ?
    #         -- AND isize.entityID = im.entityID
    #         LIMIT 1
    #     """,
    #     [file_name],
    # )
    # print(t2.fetchmany(100))
    # continue
    IMAGE_SIZE = cur.execute(
        "SELECT entityID,type, filename FROM imageSize as isize where isize.filename = ? LIMIT 1", [image_file_name]
    ).fetchone()
    # print(IMAGE_SIZE)
    # input()
    # continue
    if IMAGE_SIZE:
        enityID = IMAGE_SIZE[0]
        IMAGE = cur.execute("SELECT publishedDate,title FROM image WHERE entityID = ? LIMIT 1", [enityID]).fetchone()
        # print(IMAGE)
        if IMAGE:
            TIME = IMAGE[0]
            TIME = datetime.datetime.fromisoformat(TIME)
            return TIME.timestamp()
    return None


def find_markdown_publish_date(cur: sqlite3.Connection, markdown_file_name) -> None | float:
    IMAGE: None | tuple[str, str] = cur.execute(
        "SELECT publishedDate,title FROM image WHERE pageTitle = ? LIMIT 1", [markdown_file_name]
    ).fetchone()
    # print(IMAGE)
    if IMAGE:
        TIME = datetime.datetime.fromisoformat(IMAGE[0])
        # print(TIME)
        return TIME.timestamp()
    return None


def find_image_upload_data(cur: sqlite3.Connection, directory_path) -> Generator[tuple[str, float]]:
    directory_path = pathlib.Path(directory_path)
    assert directory_path.exists() and directory_path.is_dir()
    for a, b, c in os.walk(directory_path):
        for p in c:
            full_path = os.path.join(a, p)
            full_path2 = pathlib.Path(full_path)
            file_name = full_path2.name
            # print(full_path, file_name)
            assert file_name
            if full_path2.suffix in (".md", ".json", ".html", ""):
                TIME = find_markdown_publish_date(cur, full_path2.with_suffix("").name)
            else:
                TIME = find_image_publish_date(cur, file_name)
            if TIME is not None:
                yield full_path, TIME
            else:
                _logger.warning("No time found for %s", full_path)


def fill_with_json_data(db: sqlite3.Connection, directory_path, /, dry_run, max_depth):

    cur = db.cursor()
    # data = create_json_data(directory_path, max_depth)
    data = (
        d
        for json_obj in yield_json_from_directory(directory_path=directory_path, max_depth=max_depth)
        for d in extract_items_from_json(json_obj)
    )
    for image_data, token_data, size_data in data:
        _ = cur.execute(
            "INSERT INTO image "
            "(entityID,publishedDate,media,baseUri,prettyName,hasBlockReasons,shortUrl,Url,PageTitle,title)"
            "VALUES (?,?,?,?,?,?,?,?,?,?) "
            "RETURNING entityId",
            image_data,
        )
        _logger.debug("Inserted row: %s", cur.lastrowid)
        _ = cur.executemany("INSERT INTO token (entityId,token) VALUES (?,?)", token_data)

        _ = cur.executemany(
            "INSERT INTO imageSize (entityId,width,height,type,component,filename,radius) VALUES (?,?,?,?,?,?,?)",
            size_data,
        )
    if not dry_run:
        db.commit()
    else:
        db.rollback()


def create_json_data(directory_path, max_depth):
    directory_path = pathlib.Path(directory_path)
    assert directory_path.exists() and directory_path.is_dir()
    for a, b, c in os.walk(directory_path):
        for p in c:
            full_path = os.path.join(a, p)
            _logger.info("Parsing %s", full_path)
            with open(full_path, "r") as fp:
                try:
                    obj = json.load(fp)
                    yield from extract_items_from_json(obj)
                except json.decoder.JSONDecodeError as e:
                    _logger.warning("JSON ERROR PARSING %s, %s", full_path, e.msg)
                    continue


def yield_json_from_directory(directory_path, max_depth):

    if max_depth <= 0:
        return
    directory_path = pathlib.Path(directory_path)
    assert directory_path.exists() and directory_path.is_dir()
    for a, b, c in os.walk(directory_path):
        for p in c:
            full_path = os.path.join(a, p)
            _logger.info("Parsing %s", full_path)
            with open(full_path, "r") as fp:
                try:
                    obj = json.load(fp)
                    yield obj
                except json.decoder.JSONDecodeError as e:
                    _logger.warning("JSON ERROR PARSING %s, %s", full_path, e.msg)
                    continue
        for p in b:
            full_path_dir = os.path.join(a, p)
            _logger.info("Recursing into %s", full_path_dir)
            yield from yield_json_from_directory(full_path_dir, max_depth=max_depth - 1)


def extract_items_from_json(obj):
    def get_file_name(c, pretty_name, base_uri):
        if F := c.replace("<prettyName>", pretty_name or ""):
            return pathlib.Path(F).name
        else:
            return pathlib.Path(base_uri).name

    def create_image_size(id, x, pretty_name, base_uri):
        _logger.debug("imagesize data: %s", x)
        width = x["w"]
        height = x["h"]
        type = x["t"]
        C: str = x.get("c", "")
        F: str = get_file_name(C, pretty_name, base_uri)
        R = x["r"]
        yield id, width, height, type, C, F, R
        if extra_sizes := x.get("ss", []):
            for x2 in extra_sizes:
                w2 = x2["w"]
                h2 = x2["h"]
                t2 = f"{type}-{x2['x']}x"
                c2 = x2.get("c", "")
                f2 = get_file_name(c2, pretty_name, base_uri)
                yield id, w2, h2, t2, c2, f2, R

    deviations = obj["@@entities"]["deviation"]
    for k, v in deviations.items():
        entityId = v["entityId"]
        _logger.info("Extracting data from %s", entityId)
        publishDate = v["publishedTime"]
        media = json.dumps(v["media"])
        baseUri = v["media"].get("baseUri", "")
        prettyName = v["media"].get("prettyName", "")
        hasBlockReasons = len(v["blockReasons"]) > 0
        shortUrl = v["shortUrl"]
        url = v["url"]
        page_title = pathlib.Path(url).name
        title = v["title"]
        assert str(entityId) == str(k), f"{entityId} != {k}"
        item1 = entityId, publishDate, media, baseUri, prettyName, hasBlockReasons, shortUrl, url, page_title, title
        tokens = [(entityId, token) for token in (v["media"].get("token", []))]
        sizes = [y for x in v["media"].get("types", []) for y in create_image_size(entityId, x, prettyName, baseUri)]
        yield item1, tokens, sizes


def read_db(db: sqlite3.Connection):
    q = "SELECT entityId,title,pageTitle FROM image"
    run_query(db, q)


def read_db2(db: sqlite3.Connection):
    q = "SELECT filename,width,height,type,radius FROM imagesize"
    run_query(db, q)


def run_query(db: sqlite3.Connection, query: str):
    cur = db.cursor()
    for i, row in enumerate(cur.execute(query)):
        print(i, row, sep=": ")
    # query is read only no saving
    db.rollback()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--database", "-d", type=pathlib.Path, required=True)
    p = parser.add_mutually_exclusive_group()
    p.add_argument("--files", type=pathlib.Path)
    p.add_argument("--query", type=str)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-depth", type=int, default=1)
    parser.add_argument("--log-level", choices=logging._levelToName.values(), default="INFO")

    p2 = parser.add_mutually_exclusive_group(required=False)
    p2.add_argument("--read", action="store_true")
    p2.add_argument("--update-times", action="store_true")

    args = parser.parse_args()

    db = create_db(args.database)
    logging.basicConfig(level=args.log_level)

    if args.query:
        run_query(db, args.query)
    elif args.read:
        read_db(db)
    elif args.update_times:
        update_file_times(db, args.files, args.dry_run)
    else:
        fill_with_json_data(db, args.files, dry_run=args.dry_run, max_depth=args.max_depth)
        db.commit()
    db.close()


if __name__ == "__main__":
    main()
