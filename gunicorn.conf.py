import subprocess
import os


p = os.environ.get("PASSPHRASE")
if p:
    subprocess.Popen(["bash", "./decrypt.sh", p]).wait()

del os
del subprocess
del p


def when_ready(server):
    # touch app-initialized when ready
    try:
        open("/tmp/app-initialized", "w").close()
    except:
        pass


bind = "unix:///tmp/nginx.socket"
workers = 4
threads = 4
max_requests = 1200
max_requests_jitter = 10
timeout = 500
worker_class = "uvicorn.workers.UvicornWorker"
