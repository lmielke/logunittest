"""
    Run like:
    
    from logunittest.actions import ut as ut
    
    def run_ut(*args, **kwargs) -> str:
        # returning ut.main will return the testId
        return ut.main(*args, **kwargs)

"""
import logunittest.settings as sts
import logunittest.logunittest as lut
from logunittest.actions import stats as stats
from logunittest.general import TestParams
from subprocess import Popen
import os, subprocess, sys, time
import configparser

import colorama as color

color.init()


def main(*args, **kwargs) -> None:
    # assignes additional parameters to kwargs -> i.e. pgList, pythons
    ini0 = TestParams(*args, **kwargs)
    defaultPackage = {os.path.basename(os.getcwd()): os.getcwd()}
    print(f"{defaultPackage = }")
    run_uts(*args, **ini0.__dict__.get("pgList", defaultPackage), **kwargs)
    return kwargs["testId"]


def run_uts(*args, pgDir, pgList, **kwargs):
    for package in pgList:
        if sts.verbose >= 2:
            print(f"\ttesting: {package}, py{sys.version.split(' ')[0].strip()}")
        lut.main(*args, pgDir=package, **kwargs)


if __name__ == "__main__":
    main()
