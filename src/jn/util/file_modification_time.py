import os
from pathlib import Path
import time


def time_created_(path: Path | str) -> str:
    return os.path.getctime(path)


def time_created_readable(path: Path | str) -> str:
    time_created = time.strptime(time.ctime(time_created(path)))
    return time.strftime("%Y-%m-%d %H:%M:%S", time_created)


def time_modified(path: Path | str) -> str:
    return os.path.getmtime(path)


def time_modified_readable(path: Path | str) -> str:
    time_modified = time.strptime(time.ctime(time_modified(path)))
    return time.strftime("%Y-%m-%d %H:%M:%S", time_modified)
