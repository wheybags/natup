import natup_pkg


class v_2_29_1(natup_pkg.VersionCreator):
    def __init__(self, env: natup_pkg.Environment, name: str):
        version_str = "2.29.1"
        archive = "https://github.com/natup-packages/binutils/releases/download/2.29.1-natup-1/binutils-2.29.1-natup-1.tar.gz"
        archive_hash = "13f9cabf8f7e7dd82759ac390d3ffeaf50eeed6354bd54ccee856da7d3dd08cf"
        super().__init__(env, name, version_str, archive, archive_hash)

    def init_impl(self, env: natup_pkg.Environment):
        glibc_version_header_package = env.packages["glibc_version_header"].versions["0.1"]
        make_pkg = env.packages["make"].versions["4.2.1"]
        binutils_pkg = env.packages["binutils"].versions["2.29.1"]
        gcc_pkg = env.packages["gcc"].versions["7.2.0"]

        build_deps = {glibc_version_header_package, make_pkg, binutils_pkg, gcc_pkg}

        configure_args = ["--enable-gold", "--enable-ld=default", "--enable-plugins", "--disable-gdb"]
        build, install = natup_pkg.package_util.get_autotools_build_and_install_funcs(
            glibc_version_header_package,
            "2.13",
            extra_configure_args=configure_args)

        patch = natup_pkg.package_util.patch_gnu_project_tarball_timestamps

        self.version.finish_init(build_depends=build_deps,
                                 patch_func=patch,
                                 build_func=build,
                                 install_func=install)


def register(env: natup_pkg.Environment):
    name = "binutils"
    v_2_29_1(env, name).init(env)
