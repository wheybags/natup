import os
import shutil
import contextlib
import logging
import copy
import typing
import natup_pkg
from . import packages


class Environment:
    def __init__(self, base_path: str, is_bootstrap_env: bool = False):
        self.base_path = os.path.abspath(base_path)

        os.makedirs(self.get_src_dir(), exist_ok=True)
        os.makedirs(self.get_archive_dir(), exist_ok=True)
        os.makedirs(self.get_build_dir(), exist_ok=True)
        os.makedirs(self.get_install_dir(), exist_ok=True)

        if os.path.exists(self.get_tmp_dir()):
            shutil.rmtree(self.get_tmp_dir())

        os.makedirs(self.get_tmp_dir(), exist_ok=False)

        self.base_env_vars = copy.deepcopy(os.environ)
        self.next_tmp_file = 0

        self.is_bootstrap_env = is_bootstrap_env
        self.packages = {}

        # yes, register twice. The first time creates the packages, the second time resolves dependencies
        packages.register(self)
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

    def get_tmp_filename(self) -> str:
        self.next_tmp_file += 1
        return self.get_tmp_dir() + "/" + str(self.next_tmp_file)

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

        tmp_path = self.get_tmp_filename()

        yield tmp_path

        assert not os.path.exists(real_path)
        os.rename(tmp_path, real_path)

    def install_by_name(self, package_name: str, package_version: str = None) -> bool:
        if not self.bootstrapped():
            logging.error('natup is not bootstrapped with a base compiler. Run "natup bootstrap" to install a base' +
                          ' compiler that can then be used to compile other packages')
            return False
        if package_name not in self.packages:
            logging.error("Package not found: %s", package_name)
            return False
        if package_version is not None and package_version not in self.packages[package_name].versions:
            logging.error("Package %s version %s not found, available versions: %s",
                          package_name, package_version, list(self.packages[package_name].versions.keys()))
            return False

        if package_version is None:
            pkg = self.packages[package_name].get_latest_version()
        else:
            pkg = self.packages[package_name].versions[package_version]

        if pkg.installed(self):
            logging.info('package: %s, version: %s is already installed', pkg.package.name, pkg.version_str)
            return True

        if pkg in self.get_bootstrap_packages():
            logging.error('package: %s, version: %s is part of the boostrap packages for this os, run +'
                          ' "natup bootstrap" to install it', pkg.package.name, pkg.version_str)
            return False

        todo = [pkg]
        to_install = []

        while len(todo):
            current = todo.pop()
            to_install.append(current)
            todo += [x for x in current.depends.union(current.build_depends) if x not in to_install and x not in todo]

        to_install.reverse()

        for package in to_install:
            package.install(self)

        return True

    def get_path_for_packages(self, packages: typing.Iterable["natup_pkg.PackageVersion"], existing_path: str = None):
        path = []
        if existing_path:
            path = existing_path.split(":")
            path.reverse()

        for pkg in packages:
            path.append(pkg.get_path_var(self))

        path.reverse()

        return ":".join(path)

    def bootstrapped(self) -> bool:
        for pkg in self.get_bootstrap_packages():
            if not pkg.installed(self):
                return False

        return True

    def bootstrap(self):
        bootstrap_env = Environment(self.base_path + "/bootstrap", is_bootstrap_env=True)

        for pkg in bootstrap_env.get_bootstrap_packages():
            pkg.install(bootstrap_env)

        orig_path = self.base_env_vars["PATH"]
        self.base_env_vars["PATH"] = bootstrap_env.get_path_for_packages(bootstrap_env.get_bootstrap_packages(),
                                                                         orig_path)

        for pkg in self.get_bootstrap_packages():
            pkg.install(self)

        self.base_env_vars["PATH"] = orig_path

    def get_bootstrap_packages(self) -> typing.List["natup_pkg.PackageVersion"]:
        glibc_header_package = self.packages["glibc_version_header"].versions["0.1"]
        make_pkg = self.packages["make"].versions["4.2.1"]
        binutils_pkg = self.packages["binutils"].versions["2.29.1"]
        gcc_pkg = self.packages["gcc"].versions["7.2.0"]

        return [glibc_header_package, make_pkg, binutils_pkg, gcc_pkg]

    def get_base_env_vars(self):
        return copy.deepcopy(self.base_env_vars)
