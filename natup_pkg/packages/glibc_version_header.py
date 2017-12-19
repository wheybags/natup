import natup_pkg
import shutil


def v_0_1(pkg: natup_pkg.Package):
    version = "0.1"
    archive = "https://github.com/wheybags/glibc_version_header/archive/0.1.tar.gz"
    archive_hash = "57db74f933b7a9ea5c653498640431ce0e52aaef190d6bb586711ec4f8aa2b9e"

    def install(package: natup_pkg.PackageVersion, env: natup_pkg.Environment, install_dir: str):
        shutil.copytree(package.get_src_dir(env) + "/version_headers", install_dir)

    pkg.register_version(natup_pkg.PackageVersion(version_str=version,
                                                  archive_url=archive,
                                                  archive_hash=archive_hash,
                                                  install_func=install))


def register(env: natup_pkg.Environment):
    pkg = natup_pkg.Package("glibc_version_header")
    v_0_1(pkg)

    env.register_package(pkg)
