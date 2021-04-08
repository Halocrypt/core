from os.path import basename
from pathlib import Path
from time import sleep

from constants import CACHE_DIR

_LOCKFILE_SUFFIX = "~#.lock"


def wait_for_lock_file(filename):
    while _lockfile_exists(filename):
        sleep(0.1)
    return


def lockfile_path(original_file_name: str) -> str:
    return Path(CACHE_DIR, f"{basename(original_file_name)}{_LOCKFILE_SUFFIX}")


def create_lockfile(filename: str) -> str:
    safe_mkdir(CACHE_DIR)
    open(lockfile_path(filename), "w").close()


def close_lockfile(filename: str) -> str:
    safe_mkdir(CACHE_DIR)
    rm_path = lockfile_path(filename)
    safe_remove(rm_path)


def _lockfile_exists(filename: str) -> bool:
    return Path(lockfile_path(filename)).exists()


def open_and_read(filename: Path, should_wait_for_lockfile=False, mode="r"):
    safe_mkdir(CACHE_DIR)
    if not filename.exists():
        return None
    if should_wait_for_lockfile:
        wait_for_lock_file(filename)
    elif _lockfile_exists(filename):
        return None
    create_lockfile(filename)
    dx = filename.read_text().strip() if mode == "r" else filename.read_bytes()
    close_lockfile(filename)
    return dx or None


def open_and_write(filename: Path, data, should_wait_for_lockfile=False, mode="w"):
    safe_mkdir(CACHE_DIR)
    if should_wait_for_lockfile:
        wait_for_lock_file(filename)
    elif _lockfile_exists(filename):
        return None
    create_lockfile(filename)

    filename.write_text(data) if mode == "w" else filename.write_bytes(data)
    close_lockfile(filename)


def safe_mkdir(dir_name: str):
    Path(dir_name).mkdir(exist_ok=True)


def safe_remove(filename: str):
    try:
        Path(filename).unlink()
    except:
        pass
