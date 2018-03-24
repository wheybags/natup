import os
import typing
import natup_pkg


# Some gnu programs ship extra generated files included that are normally created as part of the build process tarballs.
# These tarballs have theirfile timestamps specially rigged so you don't need to use external programs
# to recreate generated files (eg makeinfo for docs, or bison for parser generation). We commit these extra files into
# the repos for our packages, and dump the timstamps into a timestamps.txt file so we can recreate them no matter how
# much copying or what have you has been done to the data since. (git, notably doesn't preserve file creation time)
def patch_gnu_project_tarball_timestamps(_: "natup_pkg.PackageVersion", __: "natup_pkg.Environment", src_dir: str):
    with open(src_dir + "/timestamps.txt", "rb") as f:
        lines = [x.strip() for x in f.readlines()]

    for i in range(len(lines) // 2):
        filename = lines[i * 2 + 0]
        timestamp = int(lines[i * 2 + 1])

        path = os.path.abspath(src_dir + "/" + filename.decode())
        os.utime(path, (timestamp, timestamp))


def get_autotools_build_and_install_funcs(glibc_version_header_package: "natup_pkg.PackageVersion",
                                          glibc_version: typing.Optional[str],
                                          extra_configure_args: typing.List[str] = None,
                                          extra_cflags: typing.List[str] = None,
                                          extra_cxxflags: typing.List[str] = None,
                                          extra_ldflags: typing.List[str] = None,
                                          configure_extra_env_vars: typing.Dict[str, str] = None,
                                          make_extra_env_vars: typing.Dict[str, str] = None):

    build = get_autotools_build_func(glibc_version_header_package,
                                     glibc_version,
                                     extra_configure_args,
                                     extra_cflags,
                                     extra_cxxflags,
                                     extra_ldflags,
                                     configure_extra_env_vars,
                                     make_extra_env_vars)

    return build, make_install


def get_autotools_build_func(glibc_version_header_package: "natup_pkg.PackageVersion",
                             glibc_version: typing.Optional[str],
                             extra_configure_args: typing.List[str] = None,
                             extra_cflags: typing.List[str] = None,
                             extra_cxxflags: typing.List[str] = None,
                             extra_ldflags: typing.List[str] = None,
                             configure_extra_env_vars: typing.Dict[str, str] = None,
                             make_extra_env_vars: typing.Dict[str, str] = None):

    extra_configure_args = extra_configure_args or []
    extra_cflags = extra_cflags or []
    extra_cxxflags = extra_cxxflags or []
    extra_ldflags = extra_ldflags or []

    def build(package: natup_pkg.PackageVersion, env: natup_pkg.Environment, install_dir: str):
        glibc_version_header_dir = glibc_version_header_package.get_install_dir(env)

        if glibc_version:
            glibc_version_header = glibc_version_header_dir + "/force_link_glibc_" + glibc_version + ".h"
            include_flag = "-include " + glibc_version_header
        else:
            include_flag = ""

        flags = ["CFLAGS=" + " ".join([include_flag, '-static-libgcc'] + extra_cflags),
                 "CXXFLAGS=" + " ".join([include_flag, '-static-libgcc -static-libstdc++'] + extra_cxxflags)]

        if extra_ldflags:
            flags.append("LDFLAGS=" + " ".join(extra_ldflags))

        _configure_extra_env_vars = configure_extra_env_vars or {}
        package.run_command(package.get_src_dir(env) + "/configure",
                            ["--prefix=" + install_dir] + extra_configure_args + flags,
                            package.get_build_dir(env),
                            env,
                            _configure_extra_env_vars)

        _make_extra_env_vars = make_extra_env_vars or {}
        natup_pkg.process.run('make', ['-j', str(env.get_concurrent_build_count())],
                              package.get_build_dir(env), env, _make_extra_env_vars)

    return build


def make_install(package: natup_pkg.PackageVersion, env: natup_pkg.Environment, _: str):
    package.run_command('make', ['install'], package.get_build_dir(env), env, {})
