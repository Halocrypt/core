# only for cli debugging, don't import in prod code


# pylint: disable=unused-wildcard-import
from server.app_init import *

from server.models import *

ctx = app.app_context()
ctx.push()