"""Temporary filesystem response caching  ( Optimized for flask )
"""
# this module exposes a `cache` function which caches any response returned by your
# code ( usually json ) and
# when the same route is requested again, it first checks the filesystem for the cached file
# and then directly sends it to the client instead of parsing the json again
# this makes response extremely fast as you skip a database hit as well as the json parsing and
# serialising overhead
# and sending binary using a wsgi server is pretty performant

from functools import wraps
from json import dumps, loads
from os import stat
from pathlib import Path
from time import time

from flask import make_response, send_from_directory

from constants import CACHE_DIR
from safe_io import open_and_read, open_and_write, safe_mkdir, safe_remove

DEFAULT_CACHE_TIMEOUT = 60


def file_size(fname):
    try:
        statinfo = stat(fname)
        return statinfo.st_size
    except:
        return 0


def get_file_name(key):
    return f"{key}.#cache.json"


def get_cache(key, timeout):
    fn = get_file_name(key)
    path = Path(CACHE_DIR, fn)
    data = open_and_read(path)
    if data is None:
        return None
    try:
        data = loads(data)
    except:
        safe_mkdir(path)
        return None

    ret = data["data"]
    ts = data["time_stamp"]
    if time() - ts > timeout:
        safe_remove(Path(CACHE_DIR, ret))
        return None
    if file_size(Path(CACHE_DIR, ret)):
        return ret
    return None


DATA_SUFFIX = ".___data"


def cache_json(key, data):

    fn = get_file_name(key)
    safe_mkdir(CACHE_DIR)
    path = Path(CACHE_DIR, fn)
    file_path = f"{fn}{DATA_SUFFIX}"
    js = {"time_stamp": time(), "data": file_path}
    open_and_write(path, dumps(js))
    open_and_write(
        Path(CACHE_DIR, file_path),
        dumps({"data": data} if isinstance(data, (dict, list, tuple)) else data),
    )


def cache(key_method, timeout=DEFAULT_CACHE_TIMEOUT):
    def decorator(func):
        @wraps(func)
        def json_cache(*args, **kwargs):
            key = key_method if isinstance(key_method, str) else key_method(*args)
            has_cache = get_cache(key, timeout)
            if has_cache:
                resp = make_response(send_from_directory(CACHE_DIR, has_cache))
                add_no_cache_headers(resp.headers)
                return resp
            result = func(*args, **kwargs)
            cache_json(key, result)
            return result

        return json_cache

    return decorator


def add_no_cache_headers(headers):
    # make sure that the browser does not think
    # that this is a static file sent
    # we do not want dynamic content to be cacheable
    headers["Content-Type"] = "application/json"
    headers[
        "Cache-Control"
    ] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    headers["Pragma"] = "no-cache"
    headers["Expires"] = "-1"
    headers["x-cached-response"] = "1"
    headers.remove("etag")
    headers.remove("last-modified")
