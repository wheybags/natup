import collections
import natup_pkg


class Package:
    def __init__(self, name: str):
        self.name = name
        self.versions = collections.OrderedDict()

    def register_version(self, pkg: "natup_pkg.PackageVersion"):
        assert pkg.version_str not in self.versions
        self.versions[pkg.version_str] = pkg
        pkg.set_package(self)

    def get_latest_version(self):
        return self.versions[next(reversed(self.versions))]
