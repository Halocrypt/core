from os import environ, getcwd
from os.path import join, isfile
from json import load

_CONFIG_PATH = join(getcwd(), ".env.json")


def setup_env() -> None:
    if isfile(_CONFIG_PATH):
        with open(_CONFIG_PATH, "r") as f:
            js: dict = load(f)
            environ.update(js)


del join
del getcwd
