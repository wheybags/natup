import natup_pkg


class v_7_2_0(natup_pkg.VersionCreator):
    def __init__(self, env: natup_pkg.Environment, name: str):
        version_str = "7.2.0"
        archive = "https://github.com/natup-packages/gcc/releases/download/7.2.0-natup-1/7.2.0-natup-1.tar.gz"
        archive_hash = "214797c5ea60de3527f4dc9c853a11fbbadc24479a2bcb5cc7f6d6a66bede906"
        super().__init__(env, name, version_str, archive, archive_hash)

    def init_impl(self, env: natup_pkg.Environment):
        glibc_version_header_package = env.packages["glibc_version_header"].versions["0.1"]
        make_pkg = env.packages["make"].versions["4.2.1"]
        binutils_pkg = env.packages["binutils"].versions["2.29.1"]
        gcc_pkg = env.packages["gcc"].versions["7.2.0"]  # yes, build_deps on itself

        build_deps = {glibc_version_header_package, make_pkg, binutils_pkg, gcc_pkg}
        deps = {binutils_pkg}

        configure_args = ["--enable-libstdcxx-time=rt", "--enable-languages=c,c++", "--disable-multilib",
                          "--disable-libssp", "--disable-libsanitizer"]

        glibc_ver = "2.13"
        if env.is_bootstrap_env:
            glibc_ver = None

        build, install = natup_pkg.package_util.get_autotools_build_and_install_funcs(
            glibc_version_header_package, glibc_ver, extra_configure_args=configure_args)
        patch = natup_pkg.package_util.patch_gnu_project_tarball_timestamps

        self.version.finish_init(build_depends=build_deps,
                                 depends=deps,
                                 patch_func=patch,
                                 build_func=build,
                                 install_func=install)


def register(env: natup_pkg.Environment):
    name = "gcc"
    v_7_2_0(env, name).init(env)
