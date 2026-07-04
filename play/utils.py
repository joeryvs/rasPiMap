import json
import pathlib
import weakref


class PersistentDataHolder(object):
    def __init__(self, data) -> None:
        self.data = data


def persistent_data(path, defualt):
    path = pathlib.Path(path)

    if path.exists():
        fp = open(path, "r+")
        data = json.load(fp=fp)
    else:
        fp = open(path, "w+")
        data = defualt

    def handle():
        json.dump(data, fp=fp)
        fp.close()

    item = PersistentDataHolder(data)
    # when its exit. use weakref
    weakref.finalize(item, handle)
    return item
