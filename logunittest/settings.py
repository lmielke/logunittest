# settings.py
import json, os, yaml

appName = "logunittest"
cmdsUt = ["pipenv", "run", "python", "-m", "unittest"]
# cmds_pt = ["pipenv", "run", "pytest", "--capture=sys"]
cmdsPt = ["pipenv", "run", "pytest", "--capture=sys", "-v", "-s"]

packageDir = os.path.dirname(__file__)
projectDir = os.path.dirname(packageDir)

actionsDir = os.path.join(packageDir, "actions")
actionsImportPath = f"{actionsDir.replace(projectDir, '')}".replace(os.sep, ".")[1:]

testDir = os.path.join(packageDir, "test")
testDataDir = os.path.join(testDir, "data")
# pipenv creates the text environment in the .tox folder (see tox.ini envlist)
venvsDir = os.path.join(packageDir, ".tox")
configDefault = "tox.ini"
envRegex = r"\d+\.\d+\.*\d*"  # example 3.7.4

defaultLogDir = os.path.normpath(os.path.expanduser("~/.testlogs"))
# pick one or more of the following: Logs that excede the threshold will be deleted
# set to None if a particular thresh should not apply
# NOTE: if count is set to None, no deletions or wanrings will appear due to large log count
logPreserveThreshold = {"days": 20, "count": 20}
# if verbosity is set to 1, then warnings will be issued for values threshold * warningTolerance
warningTolerance = 3

global verbose
verbose = 1

logStart = "============================= test stats start ============================="


def get_testlogsdir(*args, application=None, **kwargs):
    """
    This returns the testlogs directory for the application. If there is no application, it
    returns a zero_linked folder from testlogs.
    Note: an application represents a collection of pgList as defined in application.yml
    """
    if application is not None:
        return os.path.join(defaultLogDir, application)
    else:
        return os.path.join(defaultLogDir, "zero_linked")


def clean_params(params, *args, **kwargs):
    cleaned = []
    for param in params["pgList"]:
        cleaned.append(unalias_path(param))
    params["pgList"] = cleaned
    return params


# git_sync source is used in ut.py
gitSyncCmdgitSyncCmd = ["powershell.exe", "~/python_venvs/prc/git_sync.ps1"]
hookTypes = ["fileModification"]


def unalias_path(workPath: str) -> str:
    """
    repp³laces path aliasse such as . ~ with path text
    """
    workPath = workPath.replace(r"%USERPROFILE%", "~")
    workPath = workPath.replace("~", os.path.expanduser("~"))
    if workPath.startswith(".."):
        workPath = os.path.join(os.path.dirname(os.getcwd()), workPath[3:]).replace("/", os.sep)
    elif workPath.startswith("."):
        workPath = os.path.join(os.getcwd(), workPath[2:]).replace("/", os.sep)
    return os.path.normpath(os.path.abspath(workPath))
