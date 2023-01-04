# test_toml.py 12_21_2022__15_53_53
import logunittest.settings as sts
import os, re, sys
import toml
from copy import deepcopy

print(sys.executable)
import colorama as color

color.init()
# RUN like:
# python  C:\Users\lars\python_venvs\libs\protopy\test_toml.py
# logunittest = {editable = true, path = "/Users/Lars/python_venvs/packages/logunittest"}


class GitSyncContext:
    def __init__(self, *args, **kwargs):
        print(f"__init__: {kwargs = }")
        self.state = {}

    def __enter__(self, *args, **kwargs):
        self.pre_sync_hooks(*args, **kwargs)
        self.modify(*args, **kwargs)
        self.save(*args, modificationName="modified", **kwargs)
        return self

    def __exit__(self, *args, **kwargs):
        if os.path.exists(self.pipFilePath):
            self.save(*args, modificationName="text", **kwargs)

    def pre_sync_hooks(self, *args, **kwargs):
        self.state.update(self.update_pipfile_state(*args, **kwargs))

    def update_pipfile_state(self, *args, **kwargs):
        self.pipFilePath = os.path.join(sts.projectDir, "Pipfile")
        state = {}
        pipfileContent = toml.load(self.pipFilePath)
        pgKeys = pipfileContent["packages"].keys() & sts.availableApps.keys()
        for pgKey in pgKeys:
            # if package entry referes to the current package itself, dont modify
            if pipfileContent["packages"].get(pgKey).get("path") == ".":
                state[pgKey] = {"regex": f"({pgKey} = )" + r"({.*})"}
                state[pgKey]["local"] = pipfileContent["packages"][pgKey]
                state[pgKey]["rm"] = '{path = "."}'
            else:
                state[pgKey] = {"regex": f"({pgKey} = )" + r"({.*})"}
                state[pgKey]["local"] = pipfileContent["packages"][pgKey]
                gitUrl = (
                    f"https://{sts.params.get('apiKey')}@{sts.availableApps[pgKey][0]}/{pgKey}.git"
                )
                state[pgKey]["rm"] = "{" + f'git = "{gitUrl}"' + "}"
        return {self.pipFilePath: state}

    def modify(self, *args, **kwargs):
        """
        reads Pipfile and returns its text as well as a modified version of text
        finds a regex string as defined in self.pre_sync_hooks() and changes it
        """
        for filePath, state in self.state.items():
            with open(filePath, "r") as f:
                text = f.read()
                modified = text
            for k, vs in state.items():
                modified = re.sub(vs["regex"], r"\1" + f"{vs['rm']}", modified)
            state["text"] = text
            state["modified"] = modified

    def save(self, *args, modificationName, **kwargs):
        for filePath, state in self.state.items():
            with open(filePath, "w") as w:
                w.write(state[modificationName])
            while not os.path.exists(filePath):
                continue


"""
    gets text from a dataSafe
    NOTE: the dataSafe must contain the entry in its params.yml file
"""
