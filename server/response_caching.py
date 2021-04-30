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

from flask import make_response
from flask.helpers import send_file

from server.safe_io import (
    open_and_read,
    open_and_write,
    close_lockfile,
    safe_mkdir,
    safe_remove,
)
from server.constants import CACHE_DIR, DISABLE_CACHING

DEFAULT_CACHE_TIMEOUT = 60 * 60
DATA_SUFFIX = ".cache.json"


def file_size(fname):
    try:
        statinfo = stat(fname)
        return statinfo.st_size
    except:
        return 0


def get_file_name(key):
    return f"{key}.meta.json"


def get_cache(key, timeout):
    fn = get_file_name(key)
    path = Path(CACHE_DIR, fn)
    data = open_and_read(path)
    if data is None:
        return None
    try:
        data = loads(data)
    except Exception as e:
        print(e)
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


def get_paths(key):
    fn = get_file_name(key)
    safe_mkdir(CACHE_DIR)
    path = Path(CACHE_DIR, fn)
    file_path = Path(CACHE_DIR, f"{key}{DATA_SUFFIX}")
    return path, file_path


def cache_data(key, data):
    try:
        path, file_path = get_paths(key)
        js = {"time_stamp": time(), "data": str(file_path.resolve())}
        open_and_write(path, dumps(js).encode(), mode="wb")
        open_and_write(
            file_path,
            dumps({"data": data}).encode() if isinstance(data, (dict, list)) else data,
            mode="wb",
        )
    except Exception as e:
        print(e)
        close_lockfile(path)
        close_lockfile(file_path)


def invalidate(key):
    info, binary = get_paths(key)
    safe_remove(info)
    safe_remove(binary)
    close_lockfile(info)
    close_lockfile(binary)


def cache(key_method, timeout=DEFAULT_CACHE_TIMEOUT, json_cache: bool = False):
    def decorator(func):
        @wraps(func)
        def flask_cache(*args, **kwargs):
            if DISABLE_CACHING:
                return func(*args, **kwargs)
            key = (
                key_method
                if isinstance(key_method, str)
                else key_method(*args, **kwargs)
            )
            has_cache = get_cache(key, timeout)
            if has_cache:
                print("Cache hit:", key)
                if json_cache:
                    try:
                        return loads(Path(has_cache).read_text())["data"]
                    except:
                        pass
                else:
                    resp = get_cache_response(has_cache)
                    return resp
            print("Cache miss:", key)
            result = func(*args, **kwargs)
            cache_data(key, result)
            return result

        return flask_cache

    return decorator


def read_cache(c, mode="r"):
    return open_and_read(Path(CACHE_DIR) / c, mode=mode)


def get_cache_response(has_cache, content_type="application/json"):
    resp = make_response(send_file(has_cache))
    add_no_cache_headers(resp.headers, content_type)
    return resp


def add_no_cache_headers(headers, ct):
    # make sure that the browser does not think
    # that this is a static file sent
    # we do not want dynamic content to be cacheable
    headers["Content-Type"] = ct
    headers[
        "Cache-Control"
    ] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    headers["Pragma"] = "no-cache"
    headers["Expires"] = "-1"
    headers["x-cached-response"] = "1"
    headers.remove("etag")
    headers.remove("last-modified")
