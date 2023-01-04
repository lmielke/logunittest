import os, toml
import logunittest.settings as sts


def update_pipfile_state(*args, **kwargs):
    pipFilePath = os.path.join(sts.projectDir, "Pipfile")
    pars = {"hookType": "fileModification"}
    pipfileContent = toml.load(pipFilePath)
    pgKeys = pipfileContent["packages"].keys() & sts.availableApps.keys()
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
                f"https://{sts.params.get('apiKey')}@{sts.availableApps[pgKey][0]}/{pgKey}.git"
            )
            pars[pgKey]["rm"] = "{" + f'git = "{gitUrl}"' + "}"
    return {pipFilePath: pars}


def main(*args, **kwargs):
    return update_pipfile_state(*args, **kwargs)
