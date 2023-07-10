from .utils import get_secret

from .base import *
if get_secret('PROJECT_ENVIRONMENT') == "production":
    print('using production settings')
    from .production import *
else:
    print('using dev settings')
    from .devevlopment import *
