import subprocess
from set_env import setup_env
import os


p = os.environ.get("PASSPHRASE")
if p:
    subprocess.Popen(["bash", "./decrypt.sh", p]).wait()

setup_env()
from server.app import app

if __name__ == "__main__":

    app.run(debug=True, port=5000)
