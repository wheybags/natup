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
                                          glibc_version: str,
                                          extra_configure_args: typing.List[str] = []):
    def build(package: natup_pkg.PackageVersion, env: natup_pkg.Environment, install_dir: str):
        glibc_version_header_dir = glibc_version_header_package.get_install_dir(env)
        glibc_version_header = glibc_version_header_dir + "/force_link_glibc_" + glibc_version + ".h"

        env_vars = {
            "CFLAGS": "-include " + glibc_version_header,
            "CXXFLAGS": "-include " + glibc_version_header
        }

        natup_pkg.process.run(package.get_src_dir(env) + "/configure",
                              ["--prefix=" + install_dir] + extra_configure_args,
                              package.get_build_dir(env),
                              env,
                              env_vars)

        natup_pkg.process.run('make', ['-j', str(env.get_concurrent_build_count())],
                              package.get_build_dir(env), env, {})

    def install(package: natup_pkg.PackageVersion, env: natup_pkg.Environment, _: str):
        natup_pkg.process.run('make', ['install'], package.get_build_dir(env), env, {})

    return build, install
