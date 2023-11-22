# info.py
import logunittest.settings as sts
from logunittest.logunittest import UnitTestWithLogging, Coverage
import subprocess
import os, re, sys
import configparser

import colorama as color

color.init()


def infos(path, name, *args, **kwargs):
    msg = f"""\n{f" {name.upper()} USER info ":#^80}"""
    print(f"{color.Fore.GREEN}{msg}{color.Style.RESET_ALL}")
    with open(os.path.join(path, "setup.cfg"), "r") as f:
        info = f.read()
    print(f"info: \n{info}")


def main(*args, **kwargs):
    print(f"{kwargs = }")
    test = UnitTestWithLogging(*args, **kwargs)
    cov = Coverage(*args, **kwargs)
    print(f"\nlogs from logDir: {cov.logDir}")
    found = cov.get_stats()
    match, stats = re.match("(<@>)(.*)(<@>)", found), str()
    if match:
        for i, m in enumerate(match.group(2).split("!")):
            stats += f"{m} "
            if i == 0:
                print(f"{color.Fore.WHITE}{m}{color.Style.RESET_ALL}", end=" ")
            elif re.search(r"err:0", m):
                print(f"{color.Fore.GREEN}{m}{color.Style.RESET_ALL}")
            elif re.search(r"err:[1-9][0-9]?", m):
                print(f"{color.Fore.RED}{m}{color.Style.RESET_ALL}")
            else:
                print(f"{color.Fore.YELLOW}{m}{color.Style.RESET_ALL}")
    if not stats:
        stats = "no matching log found"
    infos(test.testPackage.pgDir, test.testPackage.pgName, *args, **kwargs)


if __name__ == "__main__":
    main()
