import importlib
import natup_pkg


def register(env: "natup_pkg.Environment"):
    importlib.import_module("natup_pkg.packages.glibc_version_header").register(env)
