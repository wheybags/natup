import natup_pkg
import shutil

name = "glibc_version_header"


def v_0_1(env: natup_pkg.Environment):
    version = "0.1"
    archive = "https://github.com/wheybags/glibc_version_header/archive/0.1.tar.gz"
    archive_hash = "57db74f933b7a9ea5c653498640431ce0e52aaef190d6bb586711ec4f8aa2b9e"

    def install(package: natup_pkg.Package, env1: natup_pkg.Environment, install_dir: str):
        shutil.copytree(package.get_src_dir(env1) + "/version_headers", install_dir)

    env.register_package(natup_pkg.Package(name=name,
                                           version_str=version,
                                           archive_url=archive,
                                           archive_hash=archive_hash,
                                           install_func=install))


def register(env: natup_pkg.Environment):
    v_0_1(env)
