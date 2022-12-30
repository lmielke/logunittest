# info.py
import logunittest.settings as sts
from logunittest.logunittest import ut as ut
from subprocess import Popen
import os, subprocess, sys
import configparser

import colorama as color

color.init()


def main(*args, targetDir, comment:str=None, git_sync:bool=False, **kwargs) -> None:
    ut(pgPath=targetDir)
    if git_sync:
        from logunittest.filestates import PipFileState
        with PipFileState(*args, targetDir=targetDir, **kwargs) as p:
            # print(f"Now pushing with modified Pipfile: {comment}")
            sts.gitSyncCmd.extend([f'"{targetDir}"', f'"{comment}"'])
            p = Popen(sts.gitSyncCmd, cwd=targetDir, stdout=sys.stdout)
            p.communicate()

if __name__ == "__main__":
    main()
