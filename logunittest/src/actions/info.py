# info.py
import logunittest.src.settings as sts
import subprocess
import os, sys
import configparser

import colorama as color

color.init()


def main(*args, packageName, **kwargs):
    msg = f"""\n{f" LOGUNITTEST USER info ":#^80}"""
    print(f"{color.Fore.GREEN}{msg}{color.Style.RESET_ALL}")
    with open(os.path.join(sts.projectPath, "setup.cfg"), "r") as f:
        info = f.read()
    print(f"info: \n{info}")
    print(f"\n you typed -p {packageName}")


if __name__ == "__main__":
    main()
