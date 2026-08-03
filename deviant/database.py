import argparse
import datetime
import json
import logging
import os
import pathlib
import sqlite3
import time
from copy import copy

_logger = logging.getLogger(__name__)


def create_db(database):

    con = sqlite3.connect(database)

    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS image(
        entityID CHAR NOT NULL ON CONFLICT FAIL UNIQUE ON CONFLICT IGNORE,
        publishedDate DATETIME NOT NULL ON CONFLICT FAIL,
        media TEXT,
        baseUri CHAR,
        prettyName CHAR,
        hasBlockReasons BOOL,
        shortUrl TEXT NOT NULL,
        url TEXT NOT NULL,
        title TEXT NOT NULL
    )
    """)
    cur.execute("""CREATE TABLE IF NOT EXISTS token(
        entityID REFERENCES images (entityID) ON DELETE CASCADE NOT NULL,
        token CHAR NOT NULL
        )
        """)
    cur.execute("""CREATE TABLE IF NOT EXISTS imageSize(
        entityID REFERENCES images (entityID) ON DELETE CASCADE NOT NULL,
        WIDTH INTEGER NOT NULL CHECK (WIDTH >= 0),
        HEIGHT INTEGER NOT NULL CHECK (HEIGHT >= 0),
        TYPE CHAR NOT NULL,
        COMPONENT CHAR,
        FILENAME CHAR,
        RADIUS INTEGER NOT NULL
        )
        """)
    con.commit()
    return con


def update_file_times(db: sqlite3.Connection, directory_path):
    rd = find_image_upload_data(db, directory_path)
    for path, create_time in rd:
        print(f"{path} will be updated to {create_time}")
        if create_time is not None:
            # print(path, datetime.datetime.fromtimestamp(create_time))
            os.utime(path=path, times=(create_time, create_time))


def find_image_upload_data(cur: sqlite3.Connection, directory_path):
    directory_path = pathlib.Path(directory_path)
    assert directory_path.exists() and directory_path.is_dir()
    for a, b, c in os.walk(directory_path):
        for p in c:
            full_path = os.path.join(a, p)
            full_path2 = pathlib.Path(full_path)
            file_name = full_path2.name
            print(full_path, file_name)
            assert file_name
            # TODO, USE 1 QUERY with a join statement
            # t2 = cur.execute(
            #     """SELECT im.publishedDate, im.title,isize.width,isize.height FROM image AS im
            #         LEFT JOIN imageSize AS isize
            #         WHERE isize.filename = ? AND isize.entityID = im.entityID
            #     """,
            #     [file_name],
            # )
            IMAGE_SIZE = cur.execute("SELECT entityID,type, filename FROM imageSize where filename = ?", [file_name]).fetchone()
            print(IMAGE_SIZE)
            if IMAGE_SIZE:
                enityID = IMAGE_SIZE[0]
                IMAGE = cur.execute("SELECT publishedDate,title FROM image WHERE entityID = ?", [enityID]).fetchone()
                print(IMAGE)
                if IMAGE:
                    TIME = IMAGE[0]
                    TIME = datetime.datetime.fromisoformat(TIME)
                    print(TIME)
                    yield full_path, TIME.timestamp()


def fill_with_json_data(db: sqlite3.Connection, directory_path):

    cur = db.cursor()
    data = create_json_data(directory_path)
    for image_data, token_data, size_data in data:
        cur.execute("INSERT INTO image VALUES (?,?,?,?,?,?,?,?,?) RETURNING entityId", image_data)
        cur.executemany("INSERT INTO token (entityId,token) VALUES (?,?)", token_data)

        cur.executemany(
            "INSERT INTO imageSize (entityId,width,height,type,component,filename,radius) VALUES (?,?,?,?,?,?,?)",
            size_data,
        )
    db.commit()


def create_json_data(directory_path):
    directory_path = pathlib.Path(directory_path)
    assert directory_path.exists() and directory_path.is_dir()
    for a, b, c in os.walk(directory_path):
        for p in c:
            full_path = os.path.join(a, p)
            print(full_path)
            with open(full_path, "r") as fp:
                try:
                    obj = json.load(fp)
                    yield from extract_items_from_json(obj)
                except json.decoder.JSONDecodeError:
                    continue


def extract_items_from_json(obj):
    def create_image_size(id, x, pretty_name, base_uri):
        width = x["w"]
        height = x["h"]
        type = x["t"]
        C: str = x.get("c", "")
        F: str = C.replace("<prettyName>", pretty_name or "")
        if F:
            F = pathlib.Path(F).name
        else:
            F = pathlib.Path(base_uri).name
        R = x["r"]
        return id, width, height, type, C, F, R

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
        title = v["title"]
        assert str(entityId) == str(k), f"{entityId} != {k}"
        item1 = entityId, publishDate, media, baseUri, prettyName, hasBlockReasons, shortUrl, url, title
        tokens = copy(v["media"].get("token", []))
        tokens = [(entityId, token) for token in tokens]
        sizes = [create_image_size(entityId, x, prettyName, baseUri) for x in v["media"].get("types", [])]
        yield item1, tokens, sizes


def read_db(db: sqlite3.Connection, params):
    cur = db.cursor()
    for i, row in enumerate(cur.execute("SELECT title,prettyName,baseUri,url,shortUrl FROM image")):
        print(i, row, sep=": ")


def read_db2(db: sqlite3.Connection, params):
    cur = db.cursor()
    for i, row in enumerate(cur.execute("SELECT filename,width,height,type,radius FROM imagesize")):
        print(i, row, sep=": ")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--database", "-d", type=pathlib.Path, required=True)
    parser.add_argument("--files", type=pathlib.Path, required=True)

    p2 = parser.add_mutually_exclusive_group(required=False)
    p3 = p2.add_argument_group()
    p3.add_argument("--read", action="store_true")
    p3.add_argument("options", type=str, nargs="*")
    p2.add_argument("--update-times", action="store_true")

    args = parser.parse_args()

    db = create_db(args.database)

    if args.read:
        print(args.options)
        read_db2(db, args.options)
    elif args.update_times:
        update_file_times(db, args.files)
    else:
        fill_with_json_data(db, args.files)
        db.commit()
    db.close()


if __name__ == "__main__":
    main()
