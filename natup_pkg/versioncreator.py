import natup_pkg


class VersionCreator:
    def __init__(self,
                 env: "natup_pkg.Environment",
                 name: str,
                 version_str: str,
                 archive: str,
                 archive_hash: str):
        if env.packages and name in env.packages:
            pkg = env.packages[name]
        else:
            pkg = natup_pkg.Package(name)
            env.register_package(pkg)

        if version_str in pkg.versions:
            self.version = pkg.versions[version_str]
            self.do_init = True
        else:
            self.version = natup_pkg.PackageVersion(version_str=version_str,
                                                    archive_url=archive,
                                                    archive_hash=archive_hash)
            pkg.register_version(self.version)
            self.do_init = False

        self.pkg = pkg

    def init(self, env: "natup_pkg.Environment"):
        if self.do_init:
            self.init_impl(env)

    def init_impl(self, env: "natup_pkg.Environment"):
        raise NotImplementedError()
