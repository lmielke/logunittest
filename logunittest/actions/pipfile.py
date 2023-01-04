# info.py
import logunittest.settings as sts
from logunittest.filestates import GitSyncContext
import os, sys, time

import colorama as color

color.init()


def main(*args, **kwargs) -> None:
    with GitSyncContext(*args, **kwargs) as p:
        for l in p.modified.split("\n"):
            print(f"{l}")


if __name__ == "__main__":
    main()
