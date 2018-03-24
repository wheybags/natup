import natup_pkg
import typing
import os
import copy


def hunter_get(build_dir: str,
               package: str,
               cmake_toolchain_filepath: str,
               extra_env_vars: typing.Dict[str, str],
               env: natup_pkg.Environment) -> str:

    cmake_build_dir = build_dir + "/hunter_" + package + "_tmp"
    os.makedirs(cmake_build_dir, exist_ok=True)

    with open(cmake_build_dir + "/HunterGate.cmake", "wb") as f:
        f.write(natup_pkg.huntergate.gate_text.encode())

    with open(cmake_build_dir + "/CMakeLists.txt", "w") as f:
        get_pkg_text = """
            cmake_minimum_required(VERSION 3.9)
            include("HunterGate.cmake")
        
            HunterGate(
                URL "https://github.com/ruslo/hunter/archive/v0.20.22.tar.gz"
                SHA1 "91e2d0346f2d3d7edcc1a036a4f7733aa5c0334d"
            )
            
            project(Hunter)
            
            hunter_add_package({0})
            
            message("PACKAGE_INSTALLED_TO::${{HUNTER_INSTALL_PREFIX}}::END")""".format(package)

        f.write(get_pkg_text)

    hunter_root = env.get_build_dir() + "/hunter_packages_root/" + package
    os.makedirs(hunter_root, exist_ok=True)

    extra_env_vars = copy.deepcopy(extra_env_vars)
    extra_env_vars["HUNTER_ROOT"] = hunter_root

    stdout = natup_pkg.process.run("cmake",
                                   ['.', '-DCMAKE_TOOLCHAIN_FILE=' + cmake_toolchain_filepath],
                                   cmake_build_dir,
                                   env,
                                   extra_env_vars)

    stdout = stdout.decode(errors='ignore')

    start = "PACKAGE_INSTALLED_TO::"
    end = "::END"

    start_idx = stdout.find(start)
    end_idx = stdout.find(end)

    if -1 in [start_idx, end_idx]:
        raise Exception("Failed to find install dir for hunter package")

    install_dir = stdout[start_idx + len(start): end_idx]
    return install_dir
