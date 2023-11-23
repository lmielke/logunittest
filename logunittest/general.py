import configparser
import platform
import subprocess
import json, os, re, time
import colorama as color

color.init()

import logunittest.settings as sts


class TestParams:
    """
    A class to manage and parse configurations from a tox.ini file.

    Attributes:
        envList (list): List of Python environment versions to test against.
        installCmd (list): Command to install dependencies.
        testCmd (list): Command to run tests.
    """

    def __init__(self, *args, envList=None, **kwargs):
        """
        Initializes the TestParams class by setting up the environment list and default commands.

        Args:
            envList (list, optional): A list of Python environment versions.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self.envList = sorted(set(envList or []), reverse=True)
        self.installCmd = ["pipenv", "install", "--dev"]
        self.testCmd = ["pipenv", "run", "lut", "ut", "-c"]
        self.load_tox_file(*args, **kwargs)

    def get_config_dir(self, *args, pgDir, application=None, **kwargs):
        """
        This returns the config directory for the application. If there is no application, it
        returns a standalone folder from testlogs.
        Note: an application represents a collection of packages as defined in application.yml
        """
        if application is None:
            return pgDir
        else:
            return sts.get_testlogsdir(*args, application=application, **kwargs)

    def load_tox_file(self, fileName=sts.configDefault, *args, **kwargs):
        """
        Loads configuration from the tox.ini file located in the specified directory.

        Args:
            pgDir (str): Directory path where tox.ini is located.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        configPath = os.path.join(self.get_config_dir(*args, **kwargs), fileName)
        config = configparser.ConfigParser()

        if config.read(configPath):
            if sts.verbose >= 2:
                print(f"{dict(config[sts.appName]) = }")
            self.load_python_versions(config, *args, **kwargs)
            self.load_commands(config, *args, **kwargs)
            self.load_logunittest_configs(config, *args, **kwargs)
        else:
            if sts.verbose >= 1:
                print(f"No {fileName} found at {configPath}")

    def load_logunittest_configs(self, config, *args, pgDir, **kwargs):
        if sts.appName in config:
            con = config[sts.appName]
            # get packages from tox.ini
            packages = con.get("pgList", self.installCmd).split(",")
            self.pgList = sts.clean_params({"pgList": [pg.strip() for pg in packages]})
            # get logging directory from tox.ini
            sts.defaultLogDir = sts.unalias_path(con.get("defaultLogDir", sts.defaultLogDir))
            sts.logPreserveThreshold = con.get("logPreserveThreshold", sts.logPreserveThreshold)
            # some additional log parameters
            if type(sts.logPreserveThreshold) is str:
                sts.logPreserveThreshold = json.loads(sts.logPreserveThreshold.replace("'", '"'))
            sts.verbose = int(con.get("verbose", sts.verbose))
        else:
            self.pgList = sts.clean_params({"pgList": [(pgDir)]})

    def load_python_versions(self, config, *args, **kwargs):
        """
        Loads Python versions from the tox.ini configuration.

        Args:
            config (ConfigParser): Parsed tox.ini configuration.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        if "tox" in config and "envlist" in config["tox"]:
            version_regex = re.compile(r"py(\d{2,3})")
            envlist = config["tox"]["envlist"].split(",")
            for env in envlist:
                match = version_regex.search(env.strip())
                if match:
                    version = match.group(1)
                    formatted_version = f"{version[0]}.{version[1:]}"
                    self.envList.append(formatted_version)
            self.envList = sorted(list(set(self.envList)), key=lambda x: x.zfill(4))

    def load_commands(self, config, *args, **kwargs):
        """
        Loads command configurations from the tox.ini file.

        Args:
            config (ConfigParser): Parsed tox.ini configuration.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        if "testenv" in config:
            self.installCmd = config["testenv"].get("install_command", self.installCmd).split()
            self.testCmd = config["testenv"].get("test_command", self.testCmd).split()

    def extend_runtime_cmd(self, cmds: list, *args, **kwargs):
        """
        Appends a command to the test command list. This is used
        by super process to submit commands/parameters to the test runner.

        Args:
            cmds: Variable length argument list.
            Example:
                params = ["-m", json.dumps(state.errors), "-i", testId]
                testInstance.extend_runtime_cmd(params)
        """
        self.testCmd.extend(cmds)
