import natup_pkg
import shutil


class v_0_1(natup_pkg.VersionCreator):
    def __init__(self, env: natup_pkg.Environment, name: str):
        version_str = "0.1"
        archive = "https://github.com/wheybags/glibc_version_header/archive/0.1.tar.gz"
        archive_hash = "57db74f933b7a9ea5c653498640431ce0e52aaef190d6bb586711ec4f8aa2b9e"
        super().__init__(env, name, version_str, archive, archive_hash)

    def init_impl(self, env: natup_pkg.Environment):
        def install(package: natup_pkg.PackageVersion, _env: natup_pkg.Environment, install_dir: str):
            shutil.copytree(package.get_src_dir(_env) + "/version_headers", install_dir)

        self.version.finish_init(install_func=install)


def register(env: natup_pkg.Environment):
    name = "glibc_version_header"
    v_0_1(env, name).init(env)
