import natup_pkg


def register(env: "natup_pkg.Environment"):
    from . import glibc_version_header
    glibc_version_header.register(env)
    from . import make
    make.register(env)
    from . import binutils
    binutils.register(env)
    from . import gcc
    gcc.register(env)
    from . import python
    python.register(env)
    from . import cmake
    cmake.register(env)
