import natup_pkg


class v_4_2_1(natup_pkg.VersionCreator):
    def __init__(self, env: natup_pkg.Environment, name: str):
        version_str = "4.2.1"
        archive = "https://github.com/natup-packages/make/releases/download/4.2.1-natup-1/make-4.2.1-natup-1.tar.gz"
        archive_hash = "06a269a4805dd31a563450fa879134278a417c90787799c306855bb2796798f8"
        super().__init__(env, name, version_str, archive, archive_hash)

    def init_impl(self, env: natup_pkg.Environment):
        glibc_version_header_package = env.packages["glibc_version_header"].versions["0.1"]
        make_pkg = env.packages["make"].versions["4.2.1"]
        binutils_pkg = env.packages["binutils"].versions["2.29.1"]
        gcc_pkg = env.packages["gcc"].versions["7.2.0"]

        build_deps = {glibc_version_header_package, make_pkg, binutils_pkg, gcc_pkg}

        glibc_ver = "2.13"
        if env.is_bootstrap_env:
            glibc_ver = None

        build, install = natup_pkg.package_util.get_autotools_build_and_install_funcs(glibc_version_header_package,
                                                                                      glibc_ver)
        patch = natup_pkg.package_util.patch_gnu_project_tarball_timestamps

        self.version.finish_init(build_depends=build_deps,
                                 patch_func=patch,
                                 build_func=build,
                                 install_func=install)


def register(env: natup_pkg.Environment):
    name = "make"
    v_4_2_1(env, name).init(env)
