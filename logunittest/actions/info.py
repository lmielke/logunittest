# info.py
import logunittest.settings as sts
from logunittest.logunittest import ProtoClass as PC
import subprocess
import os, sys
import configparser

import colorama as color

color.init()


def main(*args, **kwargs):
    msg = f"""\n{f" LOGUNITTEST USER info ":#^80}"""
    print(f"{color.Fore.GREEN}{msg}{color.Style.RESET_ALL}")
    with open(os.path.join(sts.projectPath, "setup.cfg"), "r") as f:
        info = f.read()
    print(f"info: \n{info}")

    pc = PC(*args, **kwargs)
    subprocess.call(f"python -m logunittest help".split(), shell=True)
    return pc


if __name__ == "__main__":
    main()
