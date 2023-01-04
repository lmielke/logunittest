import json, os, re, toml
import logunittest.settings as sts


def update_pipfile_sources(pipFilePath, *args, tempRmSource=None, **kwargs):
    pars = {}
    pipfileContent = toml.load(pipFilePath)
    pgKeys = pipfileContent["packages"].keys() & sts.availableApps.keys()
    if tempRmSource is not None:
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
                    f"https://{sts.params.get('apiKey')}@"
                    f"{sts.availableApps[pgKey][0]}/{pgKey}.git"
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


def main(*args, **kwargs):
    pars = {"hookType": "fileModification"}
    pipFilePath = os.path.join(sts.projectDir, "Pipfile")
    pars.update(update_pipfile_sources(pipFilePath, *args, **kwargs))
    pars.update(update_pipfile_requires(pipFilePath, *args, **kwargs))
    return {pipFilePath: pars}
