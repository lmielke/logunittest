# info.py
import logunittest.settings as sts
from logunittest.logunittest import ut as ut
import subprocess
import os, sys
import configparser

import colorama as color

color.init()


def main(*args, targetDir, **kwargs) -> None:
    ut(pgPath=targetDir)


if __name__ == "__main__":
    main()
