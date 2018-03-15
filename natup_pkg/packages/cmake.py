import natup_pkg
import shutil


class v_3_10_2(natup_pkg.VersionCreator):
    def __init__(self, env: natup_pkg.Environment, name: str):
        version_str = "3.10.2"
        archive = "https://cmake.org/files/v3.10/cmake-3.10.2-Linux-x86_64.tar.gz"
        archive_hash = "7a82b46c35f4e68a0807e8dc04e779dee3f36cd42c6387fd13b5c29fe62a69ea"
        super().__init__(env, name, version_str, archive, archive_hash)

    def init_impl(self, env: natup_pkg.Environment):
        def install(package: natup_pkg.PackageVersion, _env: natup_pkg.Environment, install_dir: str):
            shutil.copytree(package.get_src_dir(_env), install_dir)

        self.version.finish_init(install_func=install)


def register(env: natup_pkg.Environment):
    name = "cmake"
    v_3_10_2(env, name).init(env)
