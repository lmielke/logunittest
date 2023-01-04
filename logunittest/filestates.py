# test_toml.py 12_21_2022__15_53_53
import logunittest.settings as sts
import os, re, sys
import importlib
import colorama as color

color.init()
# RUN like:
# python  C:\Users\lars\python_venvs\libs\protopy\test_toml.py
# logunittest = {editable = true, path = "/Users/Lars/python_venvs/packages/logunittest"}


class GitSyncContext:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        self.state = {}

    def __enter__(self, *args, **kwargs):
        kwargs.update(self.kwargs)
        self.pre_sync_hooks(*args, **kwargs)
        self.file_modifier(*args, **kwargs)
        return self

    def __exit__(self, *args, **kwargs):
        self.save(*args, modificationName="original", **kwargs)

    def file_modifier(self, *args, **kwargs):
        """
        changes file contents on git_sync and resets dev context after push
        requires self.state to contain a modifier dictionary provided by self.pre_sync_hooks,
        Example dict to be used by self.modify:
        {'C:/Users/lars/python_venvs/packages/logunittest/Pipfile':
            {
                'hookType': 'fileModification',
                'logunittest': {
                                'regex': '(logunittest = )({.*})',
                                'local': {'editable': True, 'path': '.'},
                                'rm': '{path = "."}'}
                                }
            }
        """
        self.modify(*args, **kwargs)
        self.save(*args, modificationName="modified", **kwargs)

    def pre_sync_hooks(self, *args, **kwargs):
        for hook in os.listdir(sts.preSyncHooksDir):
            hookName = os.path.splitext(hook)[0]
            pipfile_state = importlib.import_module(f"logunittest.pre_sync_hooks.{hookName}")
            try:
                pars = pipfile_state.main(*args, **kwargs)
            except Exception as e:
                continue
            self.verify_hook_pars(pars, *args, **kwargs)
            self.state.update(pars)

    def verify_hook_pars(self, pars, *args, **kwargs):
        # pars asserts
        msg = f"pre_sync_hook must return a dictionary, but returned: {type(pars)}"
        assert type(pars) == dict, f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}"
        for k, vs in pars.items():
            msg = (
                f"pre_sync_hook dict values must contain a hookType like: "
                f"'hookType': 'fileModification', "
                f"but has: {vs.get('hookType')}"
            )
            msg = f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}"
            assert vs.get("hookType") in sts.hookTypes, msg

    def modify(self, *args, **kwargs):
        """
        reads Pipfile and returns its text as well as a modified version of text
        finds a regex string as defined in self.pre_sync_hooks() and changes it
        """
        for filePath, state in self.state.items():
            if state.get("hookType") != "fileModification":
                continue
            msg = f"fileModification-hook keys must be existing full filePaths: {filePath}"
            assert os.path.isfile(filePath), f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}"
            with open(filePath, "r") as f:
                text = f.read()
                modified = text
            # loops over all changes and applies them to text
            for k, vs in state.items():
                if k == "hookType":
                    continue
                modified = re.sub(vs["regex"], r"\1" + f"{vs['rm']}", modified)
            # file content must be appended to self.state for latter ue
            state["original"] = text
            state["modified"] = modified

    def save(self, *args, modificationName, **kwargs):
        for filePath, state in self.state.items():
            if os.path.exists(filePath):
                with open(filePath, "w") as w:
                    w.write(state[modificationName])
                while not os.path.exists(filePath):
                    continue


"""
    gets text from a dataSafe
    NOTE: the dataSafe must contain the entry in its params.yml file
"""
