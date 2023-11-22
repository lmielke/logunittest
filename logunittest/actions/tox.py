import colorama as color

color.init()
import configparser
import json, os, re, sys, time
import subprocess

# internal module imports
import logunittest.settings as sts
from logunittest.general import TestParams
import logunittest.contracts as contract


class StateManager:
    """
    Manages the creation and switching of virtual environments for different Python versions.
    """

    def __init__(self, env, *args, installCmd, pgDir, **kwargs):
        """
        Initialize the StateManager with environment details and commands.

        Args:
            env (str): The Python environment version.
            installCmd (list): Command to install dependencies in the virtual environment.
            pgDir (str): Directory path for the project.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.env = env
        self.installCmd = installCmd
        self.pgDir = sts.unalias_path(pgDir)
        self.venvFilePath, self.venvFileContent = os.path.join(self.pgDir, ".venv"), ""
        self.pipFilePath, self.pipFileContent = os.path.join(self.pgDir, "Pipfile"), ""
        self.venvDir = os.path.join(self.pgDir, ".tox", f".venv-{self.env}")
        self.errors = {__name__: {}}

    def __enter__(self, *args, **kwargs):
        """
        Context management entry point. Prepares the virtual environment for the test.
        """
        # some parameters have to be set before running the test
        self.change_pipfile(*args, **kwargs)
        self.change_venv_file(*args, **kwargs)
        # create or switch to virtual environment
        self.handle_testing_environment(*args, **kwargs)
        return self

    def change_venv_file(self, *args, **kwargs):
        # original .venv file is preserved, this should not be needed, since currently
        # there should be no .venv file in the project directory (future refactor)
        if os.path.exists(self.venvFilePath):
            with open(self.venvFilePath, "r") as venvFile:
                self.venvFileContent = venvFile.read()
        else:
            self.venvFileContent = None
        # .venv file needs to be created or updated for every test
        with open(self.venvFilePath, "w") as adjustedVenvFile:
            adjustedVenvFile.write(self.venvDir)

    def change_pipfile(self, *args, **kwargs):
        msg = f"{color.Fore.RED}{f'Invalid self.env: {self.env}'}{color.Style.RESET_ALL}"
        assert re.match(sts.envRegex, self.env), msg
        # original pipfile is preserved
        with open(self.pipFilePath, "r") as pipFile:
            self.pipFileContent = pipFile.read()
        # pipfile has to be adjusted to contain testable pyVersion i.e. python_version = "3.9"
        with open(self.pipFilePath, "w") as adjustedPipFile:
            adjustedPipFile.write(
                re.sub(
                    r"python_version\s*=\s*" + f'"{sts.envRegex}"',
                    f'python_version = "{self.env}"',
                    self.pipFileContent,
                )
            )

    def handle_testing_environment(self, *args, **kwargs):
        """
        Switches to the specified virtual environment, creating it if necessary.
        """
        # create virtual environment if it does not exist
        if not os.path.exists(self.venvDir):
            if sts.verbose >= 2:
                print(f"\nCreating venv: {self.venvDir}")
            stdout, stderr = subprocess.Popen(
                self.installCmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.pgDir,
            ).communicate()
            out, err = stdout.decode("utf-8"), stderr.decode("utf-8")
        else:
            out, err = "Already exists", ""
        # check stdout and stderr for installation errors
        self.handle_errors(out, err, *args, **kwargs)
        if sts.verbose >= 2:
            print(f"\tswitching to {self.env}")

    def handle_errors(self, out, err, *args, **kwargs):
        if not out:
            msg = f"Something went wrong Installing {self.env}!"
            print(f"{color.Fore.RED}{msg}{color.Style.RESET_ALL}")
        m = re.search(r"error.*", err, re.I)
        if m is not None:
            if sts.verbose >= 2:
                print(f"{color.Fore.RED}{m[0]}{color.Style.RESET_ALL}")
        self.errors[__name__][self.env] = f"{m[0] if m is not None else 'OK'}"

    def check_executable(self, testCmd=None, *args, **kwargs):
        """
        Verifies if the correct Python executable is being used in the virtual environment.

        Args:
            testCmd (list): Command to run tests.
        """
        # checking if the executable is in the virtual environment
        command = ["pipenv", "run", "python", "-c", "import sys; print(sys.executable)"]
        exe = subprocess.run(
            command, cwd=self.pgDir, capture_output=True, text=True
        ).stdout.strip()
        if not os.path.join(self.pgDir, ".tox", f".venv-{self.env}") in exe:
            raise Exception(f"{color.Fore.RED}Invalid path: {exe}{color.Style.RESET_ALL}")
        # checking if the executable is the correct version
        command = ["pipenv", "run", "python", "-c", "import sys; print(sys.version)"]
        python_version = subprocess.run(
            command, cwd=self.pgDir, capture_output=True, text=True
        ).stdout.strip()
        if sts.verbose >= 2:
            print(f"\tCheck {python_version.split(' ')[0]} from {exe}")

    def execute_test(self, *args, testCmd, **kwargs):
        """
        Executes the test command in the virtual environment.

        Args:
            testCmd (list): Command to run tests.
        """
        self.check_executable(testCmd, *args, **kwargs)
        subprocess.run(testCmd, cwd=self.pgDir)

    def __exit__(self, exc_type, exc_value, traceback, *args, **kwargs):
        """
        Context management exit point. Cleans up by removing the .venv file.
        """
        # remove .venv file or set it back to original
        if self.venvFileContent is None:
            if os.path.exists(self.venvFilePath):
                os.remove(self.venvFilePath)
        else:
            with open(self.venvFilePath, "w") as f:
                f.write(self.venvFileContent)
        # set Pipfile back to original
        with open(self.pipFilePath, "w") as file:
            file.write(self.pipFileContent)


def inform(ini0, *args, pgName, **kwargs):
    if sts.verbose >= 2:
        print(f"{ini0.__dict__ = }")
    pgName = pgName if pgName is not None else os.path.basename(os.getcwd())
    if sts.verbose >= 2:
        print(f"tox testing: {pgName}: {ini0.envList}")


# this function uses the StateManager and TestParams class to run the tests
def run_test(ini0, *args, testId, **kwargs):
    for i, env in enumerate(ini0.envList):
        with StateManager(env, *args, installCmd=ini0.installCmd, **kwargs) as state:
            ini0.extend_runtime_cmd(["-m", json.dumps(state.errors), "-i", testId])
            state.execute_test(*args, testCmd=ini0.testCmd, **kwargs)
    return testId


def main(*args, **kwargs) -> None:
    """
    main here is called from __main__.py module and can be run like this:
    import logunittest.actions.tox
    tox.main(*args, **kwargs)
    NOTE: for **kwargs see arguments.py
    """
    kwargs = contract.checks(*args, **kwargs)
    ini0 = TestParams(*args, **kwargs)
    inform(ini0, *args, **kwargs)
    return run_test(ini0, *args, **kwargs)
