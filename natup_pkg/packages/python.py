import natup_pkg


class v_3_6_4(natup_pkg.VersionCreator):
    def __init__(self, env: natup_pkg.Environment, name: str):
        version_str = "3.6.4"
        archive = "https://github.com/natup-packages/cpython/releases/download/3.6.4-p1/cpython-3.6.4-p1.tar.gz"
        archive_hash = "f652ff25d7dad791aac8bb82121ff48a15e1724d401012a03add5b571eb03c8b"
        super().__init__(env, name, version_str, archive, archive_hash)

    def init_impl(self, _env: natup_pkg.Environment):
        glibc_version_header_package = _env.packages["glibc_version_header"].versions["0.1"]
        make_pkg = _env.packages["make"].versions["4.2.1"]
        binutils_pkg = _env.packages["binutils"].versions["2.29.1"]
        gcc_pkg = _env.packages["gcc"].versions["7.2.0"]

        build_deps = {glibc_version_header_package, make_pkg, binutils_pkg, gcc_pkg}

        hunter_packages_env_vars = {}

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

            openssl_dir = natup_pkg.hunter.hunter_get(package.get_build_dir(env), 'OpenSSL', toolchain_path, {}, env)
            zlib_dir = natup_pkg.hunter.hunter_get(package.get_build_dir(env), 'ZLIB', toolchain_path, {}, env)
            lzma_dir = natup_pkg.hunter.hunter_get(package.get_build_dir(env), 'lzma', toolchain_path, {}, env)
            bz2_dir = natup_pkg.hunter.hunter_get(package.get_build_dir(env), 'BZip2', toolchain_path, {}, env)

            extra_ldflags = [
                # This tells the python interpreter to look for libpython in ../lib instead of system search path.
                "-Wl,-rpath,'$$ORIGIN/../lib'",

                # ctypes module uses dlopen + friends
                "-ldl"]

            extra_cflags = ["-I", zlib_dir + "/include"]

            hunter_packages_env_vars.update({
                "ZLIB_INCLUDE": zlib_dir + "/include",
                "ZLIB_LIB": zlib_dir + "/lib/libz.a",
                "LZMA_INCLUDE": lzma_dir + "/include",
                "LZMA_LIB": lzma_dir + "/lib/liblzma.a",
                "BZ2_INCLUDE": bz2_dir + "/include",
                "BZ2_LIB": bz2_dir + "/lib/libbz2.a",
                "SSL_INCLUDE": openssl_dir + "/include",
                "SSL_LIB": openssl_dir + "/lib/libssl.a",
                "SSL_CRYPTO_LIB": openssl_dir + "/lib/libcrypto.a"
            })

            autotools_build = natup_pkg.package_util.get_autotools_build_func(
                glibc_version_header_package,
                "2.13",
                # pyinstaller doesn't work with static build
                extra_configure_args=["--enable-shared", "--enable-optimization", "--with-pymalloc"],
                extra_ldflags=extra_ldflags,
                extra_cflags=extra_cflags,
                configure_extra_env_vars=hunter_packages_env_vars,
                make_extra_env_vars=hunter_packages_env_vars)

            autotools_build(package, env, install_dir)

        def install(package: natup_pkg.PackageVersion, env: natup_pkg.Environment, _: str):
            package.run_command('make', ['install'], package.get_build_dir(env), env, hunter_packages_env_vars)

        self.version.finish_init(build_depends=build_deps,
                                 build_func=build,
                                 install_func=install)


def register(env: natup_pkg.Environment):
    name = "python"
    v_3_6_4(env, name).init(env)
