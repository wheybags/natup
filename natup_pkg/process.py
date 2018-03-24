import typing
import subprocess
import natup_pkg


def run(command: str, arguments: typing.List[str], working_directory: str, env: "natup_pkg.Environment",
        extra_env_vars: typing.Dict[str, str]) -> bytes:
    """ Throws on nonzero. Prints stdout and stderr, and also returns stdout as bytes"""

    env_vars = env.get_base_env_vars()
    env_vars.update(extra_env_vars)
    # subprocess.check_call([command] + arguments, cwd=working_directory, env=env)

    cmd = [command] + arguments
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=working_directory, env=env_vars)

    stdout = []
    while proc.poll() is None:
        data = proc.stdout.readline()
        print(data.decode(errors='ignore'), end='')
        stdout.append(data)

    data = proc.stdout.read()
    print(data.decode(errors='ignore'), end='')
    stdout.append(data)

    if proc.poll() != 0:
        raise subprocess.CalledProcessError(proc.poll(), cmd)

    return b''.join(stdout)

