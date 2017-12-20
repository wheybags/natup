import typing
import subprocess
import os
import copy


def run(command: str, arguments: typing.List[str], working_directory: str, env_vars: typing.Dict[str, str]):
    env = copy.deepcopy(os.environ) #TODO get rid of this, we should construct our env from scratch
    env.update(env_vars)
    subprocess.check_call([command] + arguments, cwd=working_directory, env=env)
