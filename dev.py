import subprocess

GUNICORN_COMMANDS = (
    [
        "gunicorn",
        "-c",
        "server/gunicorn.conf.py",
        "_core:app",
        "-b",
        "localhost:5000",
    ],
    ["gunicorn", "-c", "logserver/gunicorn.conf.py", "_log:app"],
)
FLASK_COMMANDS = (
    ["python3", "_core.py"],
    ["python3", "_log.py"],
)


def get_argv(argv, i):
    try:
        return argv[i]
    except:
        return None


if __name__ == "__main__":
    import sys

    argv = sys.argv
    gunicorn = get_argv(argv, 1) == "gunicorn"
    print("Starting 2  servers")
    proc1 = subprocess.Popen(GUNICORN_COMMANDS[0] if gunicorn else FLASK_COMMANDS[0])
    proc2 = subprocess.Popen(GUNICORN_COMMANDS[1] if gunicorn else FLASK_COMMANDS[1])
    try:
        proc2.wait()
    except:
        print("Terminated, quitting")
        try:
            proc1.terminate()
            proc2.terminate()
        except:
            pass
