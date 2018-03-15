import natup_pkg


class v_3_5_2(natup_pkg.VersionCreator):
    def __init__(self, env: natup_pkg.Environment, name: str):
        version_str = "3.5.2"
        archive = "https://github.com/wheybags/python-cmake-buildsystem/releases/download/p1/python-3.5.2.tar.gz"
        archive_hash = "da38e242ec99a0dc028cd6f02b9e10904a28341007cc8d52da3358cdb890bde1"
        super().__init__(env, name, version_str, archive, archive_hash)

    def init_impl(self, env: natup_pkg.Environment):
        glibc_version_header_package = env.packages["glibc_version_header"].versions["0.1"]
        make_pkg = env.packages["make"].versions["4.2.1"]
        binutils_pkg = env.packages["binutils"].versions["2.29.1"]
        gcc_pkg = env.packages["gcc"].versions["7.2.0"]
        cmake_pkg = env.packages["cmake"].versions["3.10.2"]

        build_deps = {glibc_version_header_package, make_pkg, binutils_pkg, gcc_pkg, cmake_pkg}

        def build(package: natup_pkg.PackageVersion, env: natup_pkg.Environment, install_dir: str):
            glibc_version_header_dir = glibc_version_header_package.get_install_dir(env)
            glibc_version_header = glibc_version_header_dir + "/force_link_glibc_2.13.h"
            include_flag = "-include " + glibc_version_header

            gcc_path = gcc_pkg.get_path_var(env) + "/gcc"

            cmake_toolchain_text = """
             set(CMAKE_C "${{CMAKE_CXX_FLAGS}} {0}" CACHE STRING "" FORCE)
             set(CMAKE_EXE_LINKER_FLAGS "${{CMAKE_EXE_LINKER_FLAGS}} -static-libgcc")
             set(CMAKE_C_COMPILER "{1}")
             set(CMAKE_POSITION_INDEPENDENT_CODE YES) # force hunter package to build with -fPIC
            """.format(include_flag, gcc_path)

            toolchain_path = package.get_build_dir(env) + "/toolchain.cmake"

            with open(toolchain_path, "w") as f:
                f.write(cmake_toolchain_text)

            self.version.run_command("cmake", [package.get_src_dir(env),
                                               "-DCMAKE_TOOLCHAIN_FILE=" + toolchain_path,
                                               "-DBUILD_LIBPYTHON_SHARED=On",
                                               "-DPYTHON_VERSION=3.5.2",
                                               "-DCMAKE_INSTALL_PREFIX=" + install_dir,
                                               "-DCMAKE_BUILD_TYPE=Release"],
                                     package.get_build_dir(env),
                                     env,
                                     {})

            self.version.run_command('make', ['-j', str(env.get_concurrent_build_count())],
                                     package.get_build_dir(env), env, {})

        def install(package: natup_pkg.PackageVersion, env: natup_pkg.Environment, _: str):
            self.version.run_command('make', ['install'], package.get_build_dir(env), env, {})

        self.version.finish_init(build_depends=build_deps,
                                 build_func=build,
                                 install_func=install)


def register(env: natup_pkg.Environment):
    name = "python"
    v_3_5_2(env, name).init(env)
