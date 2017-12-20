import natup_pkg


def v_4_2_1(pkg: natup_pkg.Package, _env: natup_pkg.Environment):
    version = "4.2.1"
    archive = "file:///home/wheybags/make/4.2.1-mod.tar.gz"
    archive_hash = "none"

    glibc_version_header_package = _env.packages["glibc_version_header"].versions["0.1"]

    build, install = natup_pkg.package_util.get_autotools_build_and_install_funcs(glibc_version_header_package, "2.13")
    patch = natup_pkg.package_util.patch_gnu_project_tarball_timestamps

    pkg.register_version(natup_pkg.PackageVersion(version_str=version,
                                                  build_depends={glibc_version_header_package},
                                                  archive_url=archive,
                                                  archive_hash=archive_hash,
                                                  patch_func=patch,
                                                  build_func=build,
                                                  install_func=install))


def register(env: natup_pkg.Environment):
    pkg = natup_pkg.Package("make")
    v_4_2_1(pkg, env)

    env.register_package(pkg)
