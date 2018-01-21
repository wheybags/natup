import natup_pkg


class v_3_6_4(natup_pkg.VersionCreator):
    def __init__(self, env: natup_pkg.Environment, name: str):
        version_str = "3.6.4"
        archive = "https://www.python.org/ftp/python/3.6.4/Python-3.6.4.tgz"
        archive_hash = "7dc453e1a93c083388eb1a23a256862407f8234a96dc4fae0fc7682020227486"
        super().__init__(env, name, version_str, archive, archive_hash)

    def init_impl(self, env: natup_pkg.Environment):
        glibc_version_header_package = env.packages["glibc_version_header"].versions["0.1"]
        make_pkg = env.packages["make"].versions["4.2.1"]
        binutils_pkg = env.packages["binutils"].versions["2.29.1"]
        gcc_pkg = env.packages["gcc"].versions["7.2.0"]

        build_deps = {glibc_version_header_package, make_pkg, binutils_pkg, gcc_pkg}

        get = natup_pkg.package_util.get_autotools_build_and_install_funcs

        extra_ldflags = [
            # This tells the python interpreter to look for libpython in ../lib instead of system search path.
            "-Wl,-rpath=$$ORIGIN/../lib",

            # ctypes module uses dlopen + friends
            "-ldl"]

        build, install = get(glibc_version_header_package,
                             "2.13",
                             extra_configure_args=["--enable-shared"],  # pyinstaller doesn't work with static build
                             extra_ldflags=extra_ldflags)

        self.version.finish_init(build_depends=build_deps,
                                 build_func=build,
                                 install_func=install)


def register(env: natup_pkg.Environment):
    name = "python"
    v_3_6_4(env, name).init(env)
