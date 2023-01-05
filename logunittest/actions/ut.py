# info.py
import logunittest.settings as sts
from logunittest.logunittest import ut as ut
from logunittest.actions import stats as stats
from logunittest.filestates import GitSyncContext
from subprocess import Popen
import os, subprocess, sys, time
import configparser

import colorama as color

color.init()


def main(*args, targetDir, git_sync: bool = False, **kwargs) -> None:
    ut(*args, pgPath=targetDir, **kwargs)
    if git_sync:
        kwargs.update({"tempRmPipfileSource": True, "tempPythonVersion": "3.9"})
        comment = add_comment(*args, targetDir=targetDir, **kwargs)
        with GitSyncContext(*args, targetDir=targetDir, **kwargs) as p:
            # print(f"Now pushing with modified Pipfile: {comment}")
            time.sleep(1)
            sts.gitSyncCmd.extend([f'"{targetDir}"', f'"{comment}"'])
            p = Popen(sts.gitSyncCmd, cwd=targetDir, stdout=sys.stdout)
            p.communicate()


def add_comment(*args, comment: str = "", **kwargs) -> str:
    """
    adds a git comment in case testresults are committed and pushed to git
    """
    comment = "lut push with auto-comment" if comment is None else comment
    comment += f" [{stats.main(*args, **kwargs).split('[')[1]}"
    return comment


if __name__ == "__main__":
    main()
