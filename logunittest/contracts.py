# contracts.py
import logunittest.settings as sts
import os, re, sys
from datetime import datetime as dt
import colorama as color

color.init()


def checks(*args, **kwargs):
    warn_deletion(*args, **kwargs)
    kwargs.update(normalize_paths(*args, **kwargs))
    check_environment(*args, **kwargs)
    kwargs.update(handle_test_id(*args, **kwargs))
    return kwargs


def check_environment(*args, action=None, pgDir=None, **kwargs):
    # check if a .venv directry exists inside the project directory
    msg = f"A .venv directory already exists in {pgDir}, cant create .venv file."
    msg = f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}"
    assert not os.path.isdir(os.path.join(pgDir, ".venv")), msg
    msg = f"{color.Fore.RED}No Pipfile found in project directory!{color.Style.RESET_ALL}"
    assert os.path.isfile(os.path.join(pgDir, "Pipfile")), msg
    msg = f"{color.Fore.RED}No setup.py found in project directory!{color.Style.RESET_ALL}"
    assert os.path.isfile(os.path.join(pgDir, "setup.py")), msg
    msg = "Warning: No tox.ini found in project directory! For lut tox you will need one!"
    msg = f"{color.Fore.YELLOW}{msg}{color.Style.RESET_ALL}"
    if not os.path.isfile(os.path.join(pgDir, "tox.ini")):
        print(msg)
    msg = f"{color.Fore.RED}{msg.split(' ', 1)[1]}{color.Style.RESET_ALL}"
    assert os.path.isfile(os.path.join(pgDir, "tox.ini")) or action != "tox", msg


def assigns(*args, **kwargs):
    sts.verbose = kwargs.get("verbose")


def warn_deletion(*args, **kwargs):
    pass
    # print(f"srs.contracts.action: {action}")


def handle_test_id(*args, testId=None, **kwargs):
    if testId is None:
        testId = re.sub(r"([: .])", r"-", str(dt.now()))[:-7]
    return {"testId": testId}


def normalize_paths(*args, pgDir=None, **kwargs):
    if pgDir is None:
        pgDir = os.getcwd()
    return {"pgDir": sts.unalias_path(pgDir)}
