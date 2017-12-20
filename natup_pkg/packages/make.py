import natup_pkg


def v_4_2_1(pkg: natup_pkg.Package, _env: natup_pkg.Environment):
    version = "4.2.1"
    archive = "file:///home/wheybags/make/4.2.1-mod.tar.gz"
    archive_hash = "none"

    glibc_version_header_package = _env.packages["glibc_version_header"].versions["0.1"]

    #TODO patch step

    def build(package: natup_pkg.PackageVersion, env: natup_pkg.Environment, install_dir: str):
        glibc_version = "2.13"
        glibc_version_header_dir = glibc_version_header_package.get_install_dir(env)
        glibc_version_header = glibc_version_header_dir + "/force_link_glibc_" + glibc_version + ".h"

        env_vars = {
            "CFLAGS": "-include " + glibc_version_header,
            "CXXFLAGS": "-include " + glibc_version_header
        }

        natup_pkg.process.run(package.get_src_dir(env) + "/configure", ["--prefix=" + install_dir],
                              package.get_build_dir(env),
                              env_vars)

    def install(package: natup_pkg.PackageVersion, env: natup_pkg.Environment, _: str):
        natup_pkg.process.run('make', ['install'], package.get_build_dir(env), {})

    pkg.register_version(natup_pkg.PackageVersion(version_str=version,
                                                  build_depends={glibc_version_header_package},
                                                  archive_url=archive,
                                                  archive_hash=archive_hash,
                                                  build_func=build,
                                                  install_func=install))


def register(env: natup_pkg.Environment):
    pkg = natup_pkg.Package("make")
    v_4_2_1(pkg, env)

    env.register_package(pkg)
