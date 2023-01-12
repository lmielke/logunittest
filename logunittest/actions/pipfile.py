# info.py
import logunittest.settings as sts
from logunittest.filestates import GitSyncContext
import os, sys, time

import colorama as color

color.init()


def main(*args, targetDir=None, **kwargs) -> None:
    kwargs.update({"tempRmPipfileSource": True})
    targetDir = os.getcwd() if targetDir is None else targetDir
    pipFilePath = os.path.join(targetDir, "Pipfile")
    with GitSyncContext(*args, pipFilePath=pipFilePath, **kwargs) as p:
        assert os.path.exists(pipFilePath), f"Pipflie Not found in: {pipFilePath}"
        try:
            print(f"{p.state[pipFilePath]['modified']}")
        except Exception as e:
            print(f"Modified not found Exception: \n{e}")
            print(f"Most likely the required pre_sync_hook is missing or incomplete")


if __name__ == "__main__":
    main()
