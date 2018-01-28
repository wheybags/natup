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

        configure_args = ["--enable-libstdcxx-time=rt",
                          "--enable-languages=c,c++",
                          "--disable-multilib",
                          "--disable-libssp",
                          "--disable-libsanitizer"]

        make_extra_env_vars = {}

        glibc_ver = "2.13"
        if env.is_bootstrap_env:
            glibc_ver = None
        else:
            # gcc being a compiler has a complicated boostrapping process, to just setting CFLAGS like normal won't
            # quite cut it.

            glibc_version_header_dir = glibc_version_header_package.get_install_dir(env)
            glibc_version_header = glibc_version_header_dir + "/force_link_glibc_" + glibc_ver + ".h"
            include_flag = "-include " + glibc_version_header

            # sets flags for "target" libs, like libstdc++ (all the libs in the source tree, as far as I can tell)
            configure_args.append("CFLAGS_FOR_TARGET=" + include_flag)
            configure_args.append("CXXFLAGS_FOR_TARGET=" + include_flag)

            # sets flags for final compiler build.
            # gcc builds three times, once using the existing compiler (stage1), then again using the copy compiled in
            # stage1 (which produces stage2), then again using the stage2 compiler to build stage3 (final).
            # This sets the flags for all stages past stage1.
            # "-g -O2" is the default, so we add it in here too so it's not overwritten
            make_extra_env_vars["BOOT_CFLAGS"] = "-g -O2 " + include_flag

        build, install = natup_pkg.package_util.get_autotools_build_and_install_funcs(
            glibc_version_header_package,
            glibc_ver,
            extra_configure_args=configure_args,
            make_extra_env_vars=make_extra_env_vars)

        patch = natup_pkg.package_util.patch_gnu_project_tarball_timestamps

        self.version.finish_init(build_depends=build_deps,
                                 depends=deps,
                                 patch_func=patch,
                                 build_func=build,
                                 install_func=install)


def register(env: natup_pkg.Environment):
    name = "gcc"
    v_7_2_0(env, name).init(env)
