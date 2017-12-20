import shutil
import os
import typing
import logging
import hashlib
import natup_pkg


class PackageVersion:
    def __init__(self,
                 version_str: str = None,
                 archive_url: str = None,
                 archive_hash: str = None,
                 depends: typing.Set["natup_pkg.PackageVersion"] = None,
                 build_depends: typing.Set["natup_pkg.PackageVersion"] = None,
                 patch_func: typing.Callable[["PackageVersion", "natup_pkg.Environment", str], None] = None,
                 install_func: typing.Callable[["PackageVersion", "natup_pkg.Environment", str], None] = None,
                 build_func: typing.Callable[["natup_pkg.PackageVersion", "natup_pkg.Environment", str], None] = None):

        self.package = None
        self.version_str = version_str
        self.archive_url = archive_url
        self.archive_hash = archive_hash
        self.depends = depends if depends else set()
        self.build_depends = build_depends if build_depends else set()
        self.install_func = install_func
        self.build_func = build_func
        self.patch_func = patch_func

        assert self.version_str is not None
        assert self.archive_url is not None
        assert self.archive_hash is not None
        assert self.depends is not None
        assert self.build_depends is not None
        assert self.install_func is not None

    def set_package(self, pkg: "natup_pkg.Package"):
        assert self.package is None
        self.package = pkg

    def download_archive(self, env: "natup_pkg.Environment") -> str:
        archive_path = self.get_archive_path(env)

        if not os.path.exists(archive_path):
            logging.info("Downloading package: %s, version: %s, url: %s",
                         self.package.name, self.version_str, self.archive_url)

            with env.tmp_swap_file(archive_path) as tmp_path:
                natup_pkg.files.get(self.archive_url, tmp_path)

                hasher = hashlib.sha256()
                with open(tmp_path, "rb") as f:
                    while True:
                        data = f.read(1024 * 1024 * 16)  # 16mb

                        if not data:
                            break

                        hasher.update(data)

                file_hash = hasher.hexdigest()

                # allow skipping hash check for convenience during local development
                if self.archive_hash == 'none':
                    logging.warning("skipping hash check for package: %s, version: %s",
                                    self.package.name, self.version_str)
                    logging.warning("archive: %s", self.archive_url)
                    logging.warning("hash: %s", file_hash)
                else:
                    assert file_hash == self.archive_hash

        return archive_path

    def create_src_dir(self, env: "natup_pkg.Environment") -> str:
        archive_path = self.get_archive_path(env)
        unpack_dir = self.get_src_dir(env)

        if not os.path.exists(unpack_dir):
            logging.info("Extracting package: %s, version: %s", self.package.name, self.version_str)
            with env.tmp_swap_file(unpack_dir) as tmp_path:
                shutil.unpack_archive(archive_path, tmp_path)
                files = os.listdir(tmp_path)

                # handle archive containing a single folder
                if len(files) == 1:
                    base_path = tmp_path + "/" + files[0]
                    for f in os.listdir(base_path):
                        shutil.move(base_path + "/" + f, tmp_path)
                    os.rmdir(base_path)

                if self.patch_func is not None:
                    logging.info("Patching package: %s, version: %s", self.package.name, self.version_str)
                    self.patch_func(self, env, tmp_path)

        return unpack_dir

    def get_archive_path(self, env: "natup_pkg.Environment") -> str:
        return env.get_archive_dir() + "/" + self.package.name + "_" + self.version_str + ".tar.gz"

    def get_src_dir(self, env: "natup_pkg.Environment") -> str:
        return env.get_src_dir() + "/" + self.package.name + "_" + self.version_str

    def get_build_dir(self, env: "natup_pkg.Environment") -> str:
        return env.get_build_dir() + "/" + self.package.name + "_" + self.version_str

    def get_install_dir(self, env: "natup_pkg.Environment"):
        return env.get_install_dir() + "/" + self.package.name + "_" + self.version_str

    def installed(self, env: "natup_pkg.Environment") -> bool:
        return os.path.exists(self.get_install_dir(env))

    def install(self, env: "natup_pkg.Environment"):
        if not self.installed(env):
            self.download_archive(env)
            self.create_src_dir(env)

            if os.path.exists(self.get_build_dir(env)):
                shutil.rmtree(self.get_build_dir(env))

            with env.tmp_swap_file(self.get_install_dir(env)) as tmp_dir:
                if self.build_func is not None:
                    logging.info("Building package: %s, version: %s", self.package.name, self.version_str)
                    os.makedirs(self.get_build_dir(env))
                    self.build_func(self, env, tmp_dir)

                logging.info("Installing package: %s, version: %s", self.package.name, self.version_str)
                self.install_func(self, env, tmp_dir)
        else:
            logging.info("Skipping package: %s, version: %s, already installed", self.package.name, self.version_str)

    def __repr__(self) -> str:
        return "PackageVersion<{},{}>".format(self.package.name, self.version_str)

    def __str__(self) -> str:
        return self.__repr__()
