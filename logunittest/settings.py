# settings.py
import os, sys, time, yaml

packageDir = os.path.dirname(__file__)
projectDir = os.path.dirname(packageDir)

actionsDir = os.path.join(packageDir, "actions")
logsDir = os.path.join(packageDir, "logs")
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

