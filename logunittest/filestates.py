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
        print(f"{kwargs = }")
        self.pre_sync_hooks(*args, **kwargs)
        self.text, self.modified = self.modify()
        self.save(self.modified, self.pipFilePath)
        return self

    def __exit__(self, *args, **kwargs):
        if os.path.exists(self.pipFilePath):
            self.save(self.text, self.pipFilePath)

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
        return state

    def modify(self, *args, **kwargs):
        """
        reads Pipfile and returns its text as well as a modified version of text
        finds a regex string as defined in self.pre_sync_hooks() and changes it
        """
        with open(self.pipFilePath, "r") as f:
            text = f.read()
            modified = text
        for k, vs in self.state.items():
            modified = re.sub(vs["regex"], r"\1" + f"{vs['rm']}", modified)
        return text, modified

    def save(self, text, *args, **kwargs):
        with open(self.pipFilePath, "w") as w:
            text = w.write(text)
        while not os.path.exists(self.pipFilePath):
            continue


"""
    gets text from a dataSafe
    NOTE: the dataSafe must contain the entry in its params.yml file
"""
