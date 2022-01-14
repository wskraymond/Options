from functools import wraps
from time import time


def logger(f):
    @wraps(f)
    def wrapper(self, *args, **kw):
        ts = time()
        result = f(self, *args, **kw)
        te = time()
        print('%r, func:%r args:[%r, %r] took: %2.4f sec' % \
              (str(self), f.__name__, args, kw, te - ts))
        return result

    return wrapper
