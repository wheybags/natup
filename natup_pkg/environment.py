import os
import shutil
import contextlib
import logging
import natup_pkg
from . import packages


class Environment:
    def __init__(self, base_path: str):
        self.base_path = os.path.abspath(base_path)
        self.packages = {}

        os.makedirs(self.get_src_dir(), exist_ok=True)
        os.makedirs(self.get_archive_dir(), exist_ok=True)
        os.makedirs(self.get_build_dir(), exist_ok=True)
        os.makedirs(self.get_install_dir(), exist_ok=True)

        if os.path.exists(self.get_tmp_dir()):
            shutil.rmtree(self.get_tmp_dir())

        os.makedirs(self.get_tmp_dir(), exist_ok=False)

        self.next_tmp_file = 0

        packages.register(self)

    def get_src_dir(self) -> str:
        return self.base_path + "/source"

    def get_archive_dir(self) -> str:
        return self.base_path + "/archives"

    def get_build_dir(self) -> str:
        return self.base_path + "/build"

    def get_install_dir(self) -> str:
        return self.base_path + "/install"

    def get_tmp_dir(self) -> str:
        return self.base_path + "/tmp"

    def register_package(self, pkg: "natup_pkg.Package"):
        assert pkg.name not in self.packages
        self.packages[pkg.name] = pkg

    def get_concurrent_build_count(self):
        return 6

    @contextlib.contextmanager
    def tmp_swap_file(self, real_path: str):
        """
        For use in with statements, returns a tmp path which is copied to the real path at the end
        eg:
        with env.tmp_swap_file(env.get_build_dir() + "/whatever") as tmp_file:
            os.makedirs(tmp_file)
            with open(tmp_file + "/asd", "wb") as f:
                f.write("hi")

        The above will result in either env.get_build_dir() + "/whatever" containing a single files called asd
        contatining the text "hi", or, if there's some exception within the with body, it just won't exist at all.
        """

        self.next_tmp_file += 1
        tmp_path = self.get_tmp_dir() + "/" + str(self.next_tmp_file)

        yield tmp_path

        assert not os.path.exists(real_path)
        os.rename(tmp_path, real_path)

    def install_by_name(self, package_name: str, package_version: str = None) -> bool:
        if package_name not in self.packages:
            logging.error("Package not found: %s", package_name)
            return False
        if package_version is not None and package_version not in self.packages[package_name]:
            logging.error("Package %s version %s not found, available versions: %s",
                          package_name, self.packages[package_name].keys)

        if package_version is None:
            pkg = self.packages[package_name].get_latest_version()
        else:
            pkg = self.packages[package_name]

        todo = [pkg]
        to_install = []

        while len(todo):
            current = todo.pop()
            to_install.append(current)
            todo += [x for x in current.depends.union(current.build_depends) if x not in to_install]

        to_install.reverse()

        print(to_install)

        for package in to_install:
            package.install(self)
