import requests
import json
import tarfile
import os
import typing
import copy
import natup_pkg


class CacheProvider:
    def upload(self, env: "natup_pkg.Environment", pkg: "natup_pkg.PackageVersion"):
        raise NotImplementedError

    def download(self, env: "natup_pkg.Environment", pkg: "natup_pkg.PackageVersion"):
        raise NotImplementedError


class GithubCache(CacheProvider):
    def __init__(self, user: str, repo: str, release: str, upload_oauth_token: typing.Optional[str] = None):
        self.user = user
        self.repo = repo
        self.release = release
        self.upload_oauth_token = upload_oauth_token

    def upload(self, env: "natup_pkg.Environment", pkg: "natup_pkg.PackageVersion"):
        assert self.upload_oauth_token is not None

        auth_header = {"Authorization": "token {}".format(self.upload_oauth_token)}
        get_tag_id_url = "https://api.github.com/repos/{}/{}/releases/tags/{}".format(self.user, self.repo,
                                                                                      self.release)
        get_tag_id_response = requests.get(get_tag_id_url, headers=auth_header)
        assert get_tag_id_response.status_code == 200

        tag_id = json.loads(get_tag_id_response.text)['id']

        filename = pkg.package.name + "_" + pkg.version_str + ".tar.gz"

        get_assets_url = "https://api.github.com/repos/{}/{}/releases/{}/assets".format(self.user, self.repo, tag_id)
        get_assets_response = requests.get(get_assets_url, headers=auth_header)
        assert get_assets_response.status_code == 200
        assert filename not in [x["name"] for x in json.loads(get_assets_response.text)]

        gzfile = env.get_tmp_filename()
        with tarfile.open(gzfile, "w:gz") as tar:
            tar.add(pkg.get_install_dir(env), arcname=os.path.sep)

        upload_url = "https://uploads.github.com/repos/{}/{}/releases/{}/assets?name={}".format(self.user, self.repo,
                                                                                                tag_id, filename)
        headers = {**auth_header, "Content-Type": "application/octet-stream"}

        with open(gzfile, "rb") as f:
            upload_response = requests.post(upload_url, data=f, headers=headers)

        assert upload_response.status_code == 200

        os.remove(gzfile)


def get() -> CacheProvider:
    return GithubCache("natup-packages", "cache", "cache")


def get(provider_name: str, params: typing.Dict[str, str] = None):
    if provider_name == "github":
        oauth_token = None
        if "upload_oauth_token" in params:
            oauth_token = params["upload_oauth_token"]

        return GithubCache(params["user"], params["repo"], params["release"],
                           upload_oauth_token=oauth_token)
