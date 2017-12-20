import logging
import natup_pkg


def __main__():
    setup_logging()

    import shutil
    shutil.rmtree("test_base")
    env = natup_pkg.Environment('test_base')

    #env.install_by_name("make")
    env.install_by_name("binutils")

    #env.packages["glibc_version_header"].get_latest_version().install(env)

    # packages.glibc_version_header.foo()
    # files.get("https://google.com", "google.html")
    # files.get("file://google.html", "google2.html")


def setup_logging():
    log_format = '%(asctime)s|%(levelname)s: %(message)s'
    datefmt = '%H:%M:%S'
    logging.basicConfig(format=log_format, level=logging.INFO, datefmt=datefmt)
