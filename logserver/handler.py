from gc import collect
from os import stat, environ, path
from pathlib import Path

import requests

ACCESS_KEY = environ.get("REMOTE_LOG_DB_KEY")
LOG_FOLDER = Path(path.dirname(path.realpath(__file__)), "@logs")

del path
del environ
BYTES_IN_1MB = 1024 * 1024


def file_size(fname):
    try:
        statinfo = stat(fname)
        return statinfo.st_size
    except:
        return 0


def log_file(t: str):
    init()
    p = LOG_FOLDER / t
    p.touch(exist_ok=True)
    return p


def init():
    LOG_FOLDER.mkdir(exist_ok=True)


def push_log(t: str, line: bytes):
    file = log_file(t)
    if t == "cf" and file_size(file) / BYTES_IN_1MB >= 1:
        send_file_contents(file)
    append(file, line)
    collect()


def append(file: Path, line: bytes):
    with file.open("ab") as f:
        f.write(line)
        f.write(b"\n")


LOG_SERVER = "https://logs.halocrypt.com/add"


def send_file_contents(file: Path):
    data = file.read_bytes()
    file.write_bytes(b"")
    send_to_log_server(data)


def send_to_log_server(data: bytes):
    requests.post(
        LOG_SERVER,
        data=data,
        headers={
            "content-type": "application/octet-stream",
            "x-access-key": ACCESS_KEY,
        },
    )