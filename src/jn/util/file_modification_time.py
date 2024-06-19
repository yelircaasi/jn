import os
from pathlib import Path
import time


def time_created(path: Path | str) -> str:
    time_created = time.strptime(time.ctime(os.path.getctime(path)))
    return time.strftime("%Y-%m-%d %H:%M:%S", time_created)


def time_modified(path: Path | str) -> str:
    time_modified = time.strptime(time.ctime(os.path.getmtime(path)))
    return time.strftime("%Y-%m-%d %H:%M:%S", time_modified)
