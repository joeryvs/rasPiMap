import json
import os
import pathlib
import urllib
import urllib.parse
import uuid
import weakref


class PersistentDataHolder(object):
    def __init__(self, data) -> None:
        self.data = data


def persistent_data(path, defualt):
    path = pathlib.Path(path)

    if path.exists():
        with open(path, "r") as fp:
            data = json.load(fp=fp)
    else:
        # fp = open(path, "w")
        data = defualt

    def handle():
        with open(path, "w") as fp:
            json.dump(data, fp=fp, skipkeys=True, indent=4, allow_nan=False, check_circular=True, ensure_ascii=True)

    item = PersistentDataHolder(data)
    # when its exit. use weakref
    weakref.finalize(item, handle)
    return item


def get_extension_and_encoding(content_type: str) -> tuple[str, bool]:
    parts = content_type.split(";")
    if len(parts) >= 2:
        content_type = parts[0].strip()
    D = {
        "text/javascript": (".js", False),
        "application/javascript": (".js", False),
        "application/x-javascript": (".xjs", False),
        "application/json": (".json", True),
        "application/json+protobuf": (".json", True),
        "application/x-font-woff": (".xwoff", False),
        "image/svg+xml": (".svg", True),
        "text/plain": (".txt", False),
        "text/html": (".html", False),
        "text/css": (".css", False),
        "font/woff2": (".wf2", False),
        "image/webp": (".webp", True),
        "font/ttf": (".ttf", False),
        "image/vnd.microsoft.icon": (".ico", False),
        "image/png": (".png", True),
        "image/jpeg": (".jpeg", True),
        "image/jpg": (".jpg", True),
        "image/x-icon": (".ico", False),
        "image/gif": (".gif", True),
        "image/avif": (".avif", True),
        "video/mp4": (".mp4", True),
        "application/octet-stream": (".octet-stream", False),
    }
    return D.get(content_type, ("", False))


def save_response_handler(path, type, downloaded):

    async def handle(route):
        # print(route.request.url)
        downloaded.append(route.request.url)
        response = await route.fetch()

        ct = response.headers.get("content-type")
        x = get_extension_and_encoding(ct) if ct else ("", False)
        if len(x) != 2:
            print("ERROR, obj has no length of 2: ", x)
        if len(x) == 2:
            extension, save = x
            parsed_url = urllib.parse.urlparse(route.request.url)
            p = parsed_url.path
            downloaded.append(p)
            if not extension:
                type.append(ct)
            if save:
                p = path / uuid.uuid4().hex[:12]
                p = p.with_suffix(extension)

                body = await response.body()
                with open(p, "wb") as f:
                    f.write(body)
        await route.fulfill(response=response)

    return handle
