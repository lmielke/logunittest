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


class PipFileState:
    def __init__(self, *args, targetDir, **kwargs):
        self.pipfilePath = os.path.join(sts.unalias_path(targetDir), "Pipfile")
        self.state = self.mk_pipfile_state()
        self.text, self.modified = self.modify()

    def __enter__(self, *args, **kwargs):
        self.save(self.modified, self.pipfilePath)
        return self

    def __exit__(self, *args, **kwargs):
        if os.path.exists(self.pipfilePath):
            self.save(self.text, self.pipfilePath)

    def mk_pipfile_state(self, *args, **kwargs):
        state = {}
        pipfileContent = toml.load(self.pipfilePath)
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
        finds a regex string as defined in self.mk_pipfile_state() and changes it
        """
        with open(self.pipfilePath, "r") as f:
            text = f.read()
            modified = text
        for k, vs in self.state.items():
            modified = re.sub(vs["regex"], r"\1" + f"{vs['rm']}", modified)
        return text, modified

    def save(self, text, *args, **kwargs):
        with open(self.pipfilePath, "w") as w:
            text = w.write(text)
        while not os.path.exists(self.pipfilePath):
            continue


"""
    gets text from a dataSafe
    NOTE: the dataSafe must contain the entry in its params.yml file
"""
