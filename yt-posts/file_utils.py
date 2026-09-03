import os
import pathlib


def rename_extensionless_files_in_directory(dir: str, target_extension: str):
    assert isinstance(target_extension, str) and target_extension.startswith(".")

    directory = pathlib.Path(dir)

    assert directory.is_dir()

    for d, _dirs, files in os.walk(dir):
        for file in files:
            full_file = os.path.join(d, file)

            full_file = pathlib.Path(full_file)
            if not full_file.suffix:
                new_name = full_file.with_suffix(target_extension)
                full_file.rename(new_name)
