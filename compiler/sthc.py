import os
from sth.compiler import main


STH_STATIC_LIB = os.path.join(
        os.path.dirname(__file__),
        "c",
        "libsimplethon.a")


STH_INCLUDE_DIR = os.path.join(
        os.path.dirname(__file__),
        "c",
        "inc")


if __name__ == '__main__':
    main(lib=STH_STATIC_LIB, inc=STH_INCLUDE_DIR)
