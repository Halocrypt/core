import subprocess

GUNICORN_COMMANDS = (
    [
        "gunicorn",
        "-c",
        "gunicorn.conf.py",
        "_core:app",
        "-b",
        "localhost:5000",
    ],
)
FLASK_COMMANDS = (["python3", "_core.py"],)


def get_argv(argv, i):
    try:
        return argv[i]
    except:
        return None


if __name__ == "__main__":
    import sys

    argv = sys.argv
    gunicorn = get_argv(argv, 1) == "gunicorn"
    print("Starting")
    proc1 = subprocess.Popen(
        GUNICORN_COMMANDS[0] if gunicorn else FLASK_COMMANDS[0]
    ).wait()
