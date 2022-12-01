# settings.py
import os, sys, time, yaml

srcPath = os.path.dirname(__file__)
basePath = os.path.dirname(srcPath)
projectPath = os.path.dirname(basePath)
projectDir = os.path.dirname(projectPath)

actionsPath = os.path.join(srcPath, "actions")
testPath = os.path.join(basePath, "test")
logsPath = os.path.join(basePath, "logs")
ressourcesPath = os.path.join(basePath, "ressources")


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
