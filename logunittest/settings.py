# settings.py
import json, os

packageDir = os.path.dirname(__file__)
projectDir = os.path.dirname(packageDir)
preSyncHooksDir = os.path.join(packageDir, "pre_sync_hooks")
actionsDir = os.path.join(packageDir, "actions")
logsDir = os.path.join(packageDir, "logs")
testLogsDir = os.path.expanduser(os.path.join("~/.testlogs"))
ressourcesDir = os.path.join(packageDir, "ressources")

testDir = os.path.join(packageDir, "test")
testDataDir = os.path.join(testDir, "data")


def unalias_path(workPath: str) -> str:
    """
    repplaces path aliasse such as . ~ with path text
    """
    workPath = workPath.replace(r"%USERPROFILE%", "~")
    workPath = workPath.replace("~", os.path.expanduser("~"))
    if workPath.startswith(".."):
        workPath = os.path.join(os.path.dirname(os.getcwd()), workPath[3:]).replace("/", os.sep)
    elif workPath.startswith("."):
        workPath = os.path.join(os.getcwd(), workPath[2:]).replace("/", os.sep)
    return os.path.abspath(workPath)


# PIPFILE midifier
availableAppsPath = unalias_path(
    "~/python_venvs/modules/os_setup/droplet/configs/available_apps.json"
)
with open(availableAppsPath, "r") as j:
    availableApps = json.load(j)


# git_sync source is used in ut.py
gitSyncCmd = ["powershell.exe", "/Users/lars/python_venvs/prc/git_sync.ps1"]
hookTypes = ["fileModification"]
