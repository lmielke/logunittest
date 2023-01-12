import json, os, re, toml
import logunittest.settings as sts
from joringels.src.actions import fetch
import colorama as color

color.init()


def update_pipfile_sources(
    pipFileContent, preCommitParams, params, *args, tempRmPipfileSource=None, **kwargs
):
    pars = {}
    pgKeys = pipFileContent["packages"].keys() & sts.availableApps.keys()
    if tempRmPipfileSource is not None:
        for pgKey in pgKeys:
            # if package entry referes to the current package itself, dont modify
            if pipFileContent["packages"].get(pgKey).get("path") == ".":
                pars[pgKey] = {"regex": f"({pgKey} = )" + r"({.*})"}
                pars[pgKey]["local"] = pipFileContent["packages"][pgKey]
                pars[pgKey]["rm"] = '{path = "."}'
            else:
                pars[pgKey] = {"regex": f"({pgKey} = )" + r"({.*})"}
                pars[pgKey]["local"] = pipFileContent["packages"][pgKey]
                gitUrl = (
                    f"https://{params.get('apiKey')}@" f"{sts.availableApps[pgKey][0]}/{pgKey}.git"
                )
                pars[pgKey]["rm"] = "{" + f'git = "{gitUrl}"' + "}"
    return pars


def get_pre_commit_params(pipFileContent, *args, **kwargs):
    preCommitData, preCommitParams = pipFileContent.get("pre-commit", {}), {}
    # print(f"get_pre_commit_params: {pipFileContent = }")
    # print(f"get_pre_commit_params: {kwargs = }")
    # print(f"get_pre_commit_params: {preCommitData = }")
    for key, vs in preCommitData.items():
        section, param = key.split("_", 1)
        print(f"{section = }")
        msg = f"param: {key} must be prefixed like [pre-commit] requires_{key}"
        assert section in pipFileContent.keys(), f"{color.Fore.YELLOW}{msg}{color.Style.RESET_ALL}"
        if not preCommitParams.get(section):
            preCommitParams[section] = {param: vs}
        else:
            preCommitParams[section].update({param: vs})
    return preCommitParams


def get_sources(pipFilePath, *args, **kwargs):
    pipFileContent = toml.load(pipFilePath)
    preCommitParams = get_pre_commit_params(pipFileContent, *args, **kwargs)
    params = get_secrets(*args, **kwargs)
    sources, kwargs = prep_sources(pipFileContent, preCommitParams, params, *args, **kwargs)
    return sources, kwargs


def prep_sources(pipFileContent, preCommitParams, params, *args, **kwargs):
    """
    this takes parameter i.e. [pre-commit] and adds them to relevant sources i.e. kwargs
    to be used in update pipfile
    EXAMPLE:
    kwargs[python_version] contains the target python version i.e. "3.11"
    however, pipfile might also contain a [pre-commit] python_version which is different
    from the kwargs[python_version].
    Since kwargs take precedence the [pre-commit] version will not be used.
    if kwargs[python_version] is None, then the [pre-commit] python_version is used.

    """
    for key, vs in preCommitParams.items():
        if kwargs.get(key):
            kwargs[key] = vs
        if type(vs) == dict:
            for k, v in vs.items():
                if kwargs.get(k) is None:
                    msg = f"\nOverwriting [{key}] {k}: {kwargs[k]} -> {v}\n"
                    print(f"{color.Fore.YELLOW}{msg}{color.Style.RESET_ALL}")
                    kwargs[k] = v
    return (pipFileContent, preCommitParams, params), kwargs


def update_pipfile_python_version(
    pipFileContent, preCommitParams, params, *args, python_version=None, **kwargs
):
    """changes Pipfile
    EXAMPLE,
    Pipfile might contain:

        [requires]
        python_version = "3.11"

    and additionally might contain:

        [pre-commit]
        requires_python_version = "3.9"

    the [requires] python_version must be overwritten by [pre-commit] python_version
    """
    pars = {}
    # pipFileContent = toml.load(pipFilePath)
    for pgKey in pipFileContent["requires"].keys():
        # if package entry referes to the current package itself, dont modify
        existing = pipFileContent["requires"].get(pgKey)
        if python_version is not None and existing != python_version:
            pars[pgKey] = {"regex": r"(\npython_version = )" + r'"(\d\.\d{1,2})"'}
            pars[pgKey]["local"] = f'python_version = "{existing}"'
            pars[pgKey]["rm"] = f'"{python_version}"'
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
    sources, kwargs = get_sources(pipFilePath, *args, **kwargs)
    pars.update(update_pipfile_sources(*sources, *args, **kwargs))
    pars.update(update_pipfile_python_version(*sources, *args, **kwargs))
    return {pipFilePath: pars}
