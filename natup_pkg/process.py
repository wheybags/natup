import typing
import subprocess
import natup_pkg


def run(command: str, arguments: typing.List[str], working_directory: str, env: "natup_pkg.Environment",
        extra_env_vars: typing.Dict[str, str]):
    env = env.get_base_env_vars()
    env.update(extra_env_vars)
    subprocess.check_call([command] + arguments, cwd=working_directory, env=env)
