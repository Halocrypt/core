from pathlib import Path
from os import path

EMAIL_TEMPLATE = Path(
    path.dirname(path.realpath(__file__)), "email_template.txt"
).read_text()

del Path
del path
