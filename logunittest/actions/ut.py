# info.py
import logunittest.settings as sts
from logunittest.logunittest import ut as ut
from logunittest.actions import stats as stats
from subprocess import Popen
import os, subprocess, sys
import configparser

import colorama as color

color.init()


def main(*args, targetDir, git_sync:bool=False, **kwargs) -> None:
    ut(pgPath=targetDir)
    if git_sync:
        from logunittest.filestates import PipFileState
        comment = add_comment(*args, targetDir=targetDir, **kwargs)
        with PipFileState(*args, targetDir=targetDir, **kwargs) as p:
            # print(f"Now pushing with modified Pipfile: {comment}")
            sts.gitSyncCmd.extend([f'"{targetDir}"', f'"{comment}"'])
            p = Popen(sts.gitSyncCmd, cwd=targetDir, stdout=sys.stdout)
            p.communicate()

def add_comment(*args, comment:str='', **kwargs) -> str:
    """ 
        adds a git comment in case testresults are committed and pushed to git
    """
    comment = 'lut push without comment' if comment is None else comment
    comment += f" [{stats.main(*args, **kwargs).split('[')[1]}"
    return comment

if __name__ == "__main__":
    main()
