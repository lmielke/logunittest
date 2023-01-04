import json, os, re, toml
import logunittest.settings as sts
from joringels.src.actions import fetch


def update_pipfile_sources(pipFilePath, *args, tempRmPipfileSource=None, **kwargs):
    pars = {}
    pipfileContent = toml.load(pipFilePath)
    pgKeys = pipfileContent["packages"].keys() & sts.availableApps.keys()
    params = get_secrets(*args, **kwargs)
    if tempRmPipfileSource is not None:
        for pgKey in pgKeys:
            # if package entry referes to the current package itself, dont modify
            if pipfileContent["packages"].get(pgKey).get("path") == ".":
                pars[pgKey] = {"regex": f"({pgKey} = )" + r"({.*})"}
                pars[pgKey]["local"] = pipfileContent["packages"][pgKey]
                pars[pgKey]["rm"] = '{path = "."}'
            else:
                pars[pgKey] = {"regex": f"({pgKey} = )" + r"({.*})"}
                pars[pgKey]["local"] = pipfileContent["packages"][pgKey]
                gitUrl = (
                    f"https://{params.get('apiKey')}@" f"{sts.availableApps[pgKey][0]}/{pgKey}.git"
                )
                pars[pgKey]["rm"] = "{" + f'git = "{gitUrl}"' + "}"
    return pars


def update_pipfile_requires(pipFilePath, *args, tempPythonVersion=None, **kwargs):
    pars = {}
    pipfileContent = toml.load(pipFilePath)
    for pgKey in pipfileContent["requires"].keys():
        # if package entry referes to the current package itself, dont modify
        existing = pipfileContent["requires"].get(pgKey)
        if tempPythonVersion is not None and existing != tempPythonVersion:
            pars[pgKey] = {"regex": r"(python_version = )" + r'"(\d\.\d{1,2})"'}
            pars[pgKey]["local"] = f'python_version = "{existing}"'
            pars[pgKey]["rm"] = f'"{tempPythonVersion}"'
    return pars


def get_secrets(*args, **kwargs):
    # params are used to modify pipfile_state in filestates.GitSyncContext.mk_pipfile_state
    params = {}
    try:
        repoParams = fetch.alloc(entryName="repo_download", retain=True)
        params.update({"apiKey": repoParams["password"]})
    except:
        params.update({"apiKey": "Not found"})
    return params


def main(*args, pipFilePath: str = None, **kwargs):
    pars = {"hookType": "fileModification"}
    pipFilePath = os.path.join(os.getcwd(), "Pipfile") if pipFilePath is None else pipFilePath
    pars.update(update_pipfile_sources(pipFilePath, *args, **kwargs))
    pars.update(update_pipfile_requires(pipFilePath, *args, **kwargs))
    return {pipFilePath: pars}
